#include <arpa/inet.h>
#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <map>
#include <mutex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <sys/socket.h>
#include <thread>
#include <unistd.h>

std::map<int, std::string> coupons;
std::mutex coupon_mutex;
std::atomic<int> next_id{1};

std::string decode(const std::string& value) {
    std::string out;
    for (size_t i = 0; i < value.size(); ++i) {
        if (value[i] == '+') out += ' ';
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
        auto position = item.find('=');
        result[decode(item.substr(0, position))] = position == std::string::npos ? "" : decode(item.substr(position + 1));
    }
    return result;
}

void reply(int client, int status, const std::string& body) {
    std::string reason = status == 200 ? "OK" : status == 201 ? "Created" : "Bad Request";
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
    std::stringstream first(request.substr(0, request.find("\r\n")));
    std::string method, uri, version;
    first >> method >> uri >> version;
    auto query_at = uri.find('?');
    auto path = uri.substr(0, query_at);
    auto query = query_at == std::string::npos ? std::string() : uri.substr(query_at + 1);
    auto body_at = request.find("\r\n\r\n");
    auto body = body_at == std::string::npos ? std::string() : request.substr(body_at + 4);
    try {
        if (method == "GET" && path == "/health") reply(client, 200, "{\"status\":\"ok\"}");
        else if (method == "POST" && path == "/api/coupons") {
            auto form = params(body);
            auto secret = form.at("secret");
            if (secret.empty() || secret.size() > 4096) throw std::runtime_error("bad secret");
            int id = next_id++;
            { std::lock_guard<std::mutex> guard(coupon_mutex); coupons[id] = secret; }
            reply(client, 201, "{\"id\":" + std::to_string(id) + "}");
        } else if (method == "GET" && path == "/api/coupons") {
            std::string result = "[";
            std::lock_guard<std::mutex> guard(coupon_mutex);
            for (const auto& [id, unused] : coupons) {
                if (result.size() > 1) result += ',';
                result += std::to_string(id);
            }
            reply(client, 200, result + "]");
        } else if (method == "GET" && path == "/api/receipt") {
            auto values = params(query);
            int id = std::stoi(values.at("id"));
            auto label = values.at("label");
            std::string secret;
            { std::lock_guard<std::mutex> guard(coupon_mutex); secret = coupons.at(id); }
            char output[8192];
            std::snprintf(output, sizeof(output), label.c_str(), secret.c_str());
            reply(client, 200, "{\"receipt\":\"" + std::string(output) + "\"}");
        } else reply(client, 400, "{\"error\":\"unknown request\"}");
    } catch (...) { reply(client, 400, "{\"error\":\"invalid request\"}"); }
    close(client);
}

int main() {
    int server = socket(AF_INET, SOCK_STREAM, 0), enabled = 1;
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
