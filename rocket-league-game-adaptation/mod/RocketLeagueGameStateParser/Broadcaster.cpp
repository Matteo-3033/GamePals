#include "pch.h"
#include "Broadcaster.h"

#include <vector>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <mutex>
#include <thread>
#include "logging.h"

#pragma comment(lib, "ws2_32.lib")

broadcaster::broadcaster()
{
    WSADATA wsa_data;
    if (WSAStartup(MAKEWORD(2, 2), &wsa_data) != 0) {
		throw std::runtime_error("WSAStartup failed");
    }

    server_ = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (server_ == INVALID_SOCKET) {
        WSACleanup();
		throw std::runtime_error("Socket creation failed");
    }
}

void broadcaster::start(const std::string& host, const u_short port)
{
    if (running_)
        return;

    LOG("Initializing socket on {}:{}...", host, port);

    auto server_address = sockaddr_in();
    server_address.sin_family = AF_INET;
    server_address.sin_port = htons(port);

    if (inet_pton(AF_INET, host.c_str(), &server_address.sin_addr) <= 0) {
        LOG("Invalid address/Address not supported\n");
		throw std::runtime_error("Invalid address/Address not supported");
    }

	if (bind(server_, reinterpret_cast<sockaddr*>(&server_address), sizeof(server_address)) == SOCKET_ERROR) {
        LOG("Socket bind failed\n");
		throw std::runtime_error("Socket bind failed");
	}

    if (listen(server_, SOMAXCONN) == SOCKET_ERROR) {
        LOG("Socket listen failed\n");
		throw std::runtime_error("Socket listen failed");
    }

    LOG("Socket initialized");

    running_ = true;
    accept_thread_ = std::thread(&broadcaster::accept_clients, this);
    broadcast_thread_ = std::thread(&broadcaster::broadcast_loop, this);
}

void broadcaster::accept_clients()
{
	LOG("Socket accepting clients...\n");

    while (running_) {
        SOCKET socket = accept(server_, nullptr, nullptr);
        if (socket == INVALID_SOCKET) {
            LOG("Accept failed\n");
            continue;
        }

		LOG("Client connected\n");

        std::lock_guard<std::mutex> lock(client_mutex_);
        client_sockets_.push_back(socket);
    }
}

void broadcaster::enqueue_message(std::string&& msg)
{
    {
        std::lock_guard lock(queue_mutex_);
        message_queue_.push(std::move(msg));
    }

    queue_cv_.notify_one();
}

void broadcaster::broadcast_loop()
{
    while (running_)
    {
        std::unique_lock lock(queue_mutex_);
        queue_cv_.wait(lock, [this] { return !message_queue_.empty() || !running_; });

        if (!running_ && message_queue_.empty())
            break;

        std::string msg = std::move(message_queue_.front());
        message_queue_.pop();
        lock.unlock();

        std::lock_guard client_lock(client_mutex_);
        const uint32_t length = htonl(msg.size());
        std::vector<SOCKET> to_remove;

        for (const SOCKET& client : client_sockets_)
        {
            int ok = send(client, reinterpret_cast<const char*>(&length), sizeof(uint32_t), 0);

            if (ok != SOCKET_ERROR)
                ok = send(client, msg.c_str(), msg.size(), 0);

            if (ok == SOCKET_ERROR)
                to_remove.push_back(client);
        }

        for (SOCKET client : to_remove)
        {
            closesocket(client);
            std::erase(client_sockets_, client);
        }
    }
}

void broadcaster::stop()
{
	if (!running_)
		return;

	running_ = false;

    queue_cv_.notify_all();

    if (accept_thread_.joinable())
        accept_thread_.join();

    if (broadcast_thread_.joinable())
        broadcast_thread_.join();

    {
        std::lock_guard lock(client_mutex_);
        for (SOCKET client : client_sockets_)
            closesocket(client);
    }
    
    if (server_ != INVALID_SOCKET)
        closesocket(server_);
}

broadcaster::~broadcaster()
{
	stop();
    WSACleanup();
}
