#pragma once

#include <string>
#include <vector>
#include <queue>
#include <condition_variable>
#include <winsock2.h>
#include <mutex>
#include <thread>

#include <nlohmann/json.hpp>

class broadcaster
{

public:
	broadcaster();
	~broadcaster();

	void start(const std::string& host = "127.0.0.1", u_short port = 3000);
	template<typename T> void broadcast(const T& obj);
	void stop();

private:
	void accept_clients();
	void broadcast_loop();
	void enqueue_message(std::string&& msg);

	bool running_ = false;

	SOCKET server_ = INVALID_SOCKET;

	std::vector<SOCKET> client_sockets_;
	std::mutex client_mutex_;

	std::thread accept_thread_;
	std::thread broadcast_thread_;

	std::queue<std::string> message_queue_;
	std::mutex queue_mutex_;
	std::condition_variable queue_cv_;
};

template<typename T>
void broadcaster::broadcast(const T& obj)
{
	nlohmann::json j = obj;
	std::string message = j.dump();

	enqueue_message(std::move(message));
}
