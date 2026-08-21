#pragma once
#include "SaveData.hpp"
#include <string>

class SaveManager
{
    public:
        static void save(const SaveData& data);
        static SaveData load();
};

