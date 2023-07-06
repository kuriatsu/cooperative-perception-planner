#pragma once
#include "ras.h"
#include "despot/interface/world.h"
#include "sumo_interface.h"
#include "operator_model.h"
#include "libgeometry.h"

using namespace despot;

class RasWorld: public World {
private:
    State* pomdp_state;
    std::vector<std::string> id_idx_list;
    int REQUEST = 0, NO_ACTION, RECOG;
    int NONE = 2;

public:
    SumoInterface sim;
    OperatorModel operator_model;

public:
    bool Connect();
    State* Initialize();
    State* GetCurrentState(const std::vector<Pose>& targets);
    bool ExecuteAction(ACT_TYPE action, OBS_TYPE& obs);
    void updateBeliefState(ACT_TYPE action, OBS_TYPE obs, const std::vector<double>& risk_probs);
    ~World();
} 

