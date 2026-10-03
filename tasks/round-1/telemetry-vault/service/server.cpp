#include <arpa/inet.h>
#include <atomic>
#include <cctype>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <map>
#include <mutex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <sys/socket.h>
#include <thread>
#include <unistd.h>
#include <vector>

struct Message { long long owner; std::string text; };
std::map<int, Message> messages;
std::mutex messages_mutex;
std::atomic<int> next_id{1};

std::string decode(const std::string& value) {
    std::string out;
    for (size_t i = 0; i < value.size(); ++i) {
        if (value[i] == '+' ) out += ' ';
        else if (value[i] == '%' && i + 2 < value.size()) {
            out += static_cast<char>(std::strtol(value.substr(i + 1, 2).c_str(), nullptr, 16));
            i += 2;
        } else out += value[i];
    }
    return out;
}

std::map<std::string, std::string> params(const std::string& text) {
    std::map<std::string, std::string> result;
    std::stringstream stream(text);
    std::string item;
    while (std::getline(stream, item, '&')) {
        auto equals = item.find('=');
        result[decode(item.substr(0, equals))] = equals == std::string::npos ? "" : decode(item.substr(equals + 1));
    }
    return result;
}

void reply(int client, int status, const std::string& body) {
    std::string reason = status == 200 ? "OK" : status == 201 ? "Created" : status == 403 ? "Forbidden" : "Bad Request";
    std::string response = "HTTP/1.1 " + std::to_string(status) + " " + reason + "\r\nContent-Type: application/json\r\nContent-Length: " + std::to_string(body.size()) + "\r\nConnection: close\r\n\r\n" + body;
    send(client, response.data(), response.size(), 0);
}

void handle(int client) {
    std::string request;
    char buffer[4096];
    while (request.size() < 65536) {
        ssize_t count = recv(client, buffer, sizeof(buffer), 0);
        if (count <= 0) break;
        request.append(buffer, count);
        auto split = request.find("\r\n\r\n");
        if (split != std::string::npos) {
            auto marker = request.find("Content-Length:");
            size_t length = marker == std::string::npos ? 0 : std::stoul(request.substr(marker + 15));
            if (request.size() >= split + 4 + length) break;
        }
    }
    auto line_end = request.find("\r\n");
    auto first = request.substr(0, line_end);
    std::stringstream line(first);
    std::string method, uri, version;
    line >> method >> uri >> version;
    auto query_at = uri.find('?');
    auto path = uri.substr(0, query_at);
    auto query = query_at == std::string::npos ? std::string() : uri.substr(query_at + 1);
    auto body_at = request.find("\r\n\r\n");
    auto body = body_at == std::string::npos ? std::string() : request.substr(body_at + 4);
    try {
        if (method == "GET" && path == "/health") reply(client, 200, "{\"status\":\"ok\"}");
        else if (method == "POST" && path == "/api/messages") {
            auto form = params(body);
            long long owner = std::stoll(form.at("owner"));
            if (form.at("text").empty() || form.at("text").size() > 4096) throw std::runtime_error("bad text");
            int id = next_id++;
            { std::lock_guard<std::mutex> guard(messages_mutex); messages[id] = {owner, form.at("text")}; }
            reply(client, 201, "{\"id\":" + std::to_string(id) + "}");
        } else if (method == "GET" && path == "/api/messages") {
            std::string result = "[";
            std::lock_guard<std::mutex> guard(messages_mutex);
            for (const auto& [id, message] : messages) {
                if (result.size() > 1) result += ',';
                result += "{\"id\":" + std::to_string(id) + ",\"owner_hint\":" + std::to_string(static_cast<uint16_t>(message.owner)) + "}";
            }
            reply(client, 200, result + "]");
        } else if (method == "GET" && path == "/api/messages/read") {
            auto values = params(query);
            int id = std::stoi(values.at("id"));
            long long owner = std::stoll(values.at("owner"));
            std::lock_guard<std::mutex> guard(messages_mutex);
            auto found = messages.find(id);
            if (found == messages.end()) throw std::runtime_error("missing");
            if (static_cast<uint16_t>(owner) != static_cast<uint16_t>(found->second.owner)) reply(client, 403, "{\"error\":\"wrong owner\"}");
            else reply(client, 200, "{\"text\":\"" + found->second.text + "\"}");
        } else reply(client, 400, "{\"error\":\"unknown request\"}");
    } catch (...) { reply(client, 400, "{\"error\":\"invalid request\"}"); }
    close(client);
}

int main() {
    int server = socket(AF_INET, SOCK_STREAM, 0);
    int enabled = 1;
    setsockopt(server, SOL_SOCKET, SO_REUSEADDR, &enabled, sizeof(enabled));
    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(8000);
    if (bind(server, reinterpret_cast<sockaddr*>(&address), sizeof(address)) < 0 || listen(server, 64) < 0) return 1;
    while (true) {
        int client = accept(server, nullptr, nullptr);
        if (client >= 0) std::thread(handle, client).detach();
    }
}
