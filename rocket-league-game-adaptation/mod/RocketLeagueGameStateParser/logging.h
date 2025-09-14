// ReSharper disable CppNonExplicitConvertingConstructor
#pragma once
#include <string>
#include <source_location>
#include <format>
#include <memory>

#include "bakkesmod/wrappers/cvarmanagerwrapper.h"

extern std::shared_ptr<CVarManagerWrapper> global_cvar_manager;
constexpr bool DEBUG_LOG = false;


struct format_string
{
	std::string_view str;
	std::source_location loc{};

	format_string(const char* str, const std::source_location& loc = std::source_location::current()) : str(str), loc(loc)
	{
	}

	format_string(const std::string&& str, const std::source_location& loc = std::source_location::current()) : str(str), loc(loc)
	{
	}

	[[nodiscard]] std::string get_location() const
	{
		return std::format("[{} ({}:{})]", loc.function_name(), loc.file_name(), loc.line());
	}
};

struct format_wstring
{
	std::wstring_view str;
	std::source_location loc{};

	format_wstring(const wchar_t* str, const std::source_location& loc = std::source_location::current()) : str(str), loc(loc)
	{
	}

	format_wstring(const std::wstring&& str, const std::source_location& loc = std::source_location::current()) : str(str), loc(loc)
	{
	}

	[[nodiscard]] std::wstring get_location() const
	{
		auto basic_string = std::format("[{} ({}:{})]", loc.function_name(), loc.file_name(), loc.line());
		return { basic_string.begin(), basic_string.end() };
	}
};


template <typename... Args>
void LOG(const std::string_view& format_str, Args&&... args)
{
	global_cvar_manager->log(std::vformat(format_str, std::make_format_args(args...)));
}

template <typename... Args>
void LOG(const std::wstring_view& format_str, Args&&... args)
{
	global_cvar_manager->log(std::vformat(format_str, std::make_wformat_args(args...)));
}


template <typename... Args>
void DEBUGLOG(const format_string& format_str, Args&&... args)
{
	if constexpr (DEBUG_LOG)
	{
		auto text = std::vformat(format_str.str, std::make_format_args(args...));
		auto location = format_str.get_location();
		global_cvar_manager->log(std::format("{} {}", text, location));
	}
}

template <typename... Args>
void DEBUGLOG(const format_wstring& format_str, Args&&... args)
{
	if constexpr (DEBUG_LOG)
	{
		auto text = std::vformat(format_str.str, std::make_wformat_args(args...));
		auto location = format_str.get_location();
		global_cvar_manager->log(std::format(L"{} {}", text, location));
	}
}
