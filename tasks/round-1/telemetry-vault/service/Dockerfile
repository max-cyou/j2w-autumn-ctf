FROM alpine:3.22 AS build
WORKDIR /src
RUN apk add --no-cache g++
COPY server.cpp .
RUN g++ -O2 -std=c++20 -pthread -o /server server.cpp
FROM alpine:3.22
RUN apk add --no-cache libstdc++
COPY --from=build /server /server
USER 65534:65534
CMD ["/server"]
