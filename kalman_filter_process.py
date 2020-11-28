import numpy as np
import pandas as pd
from pykalman import UnscentedKalmanFilter



# constants not part of the state
# todo set as per our data, this is sampling time
h = 5


def transition_function(state, noise):
    # assuming that the noise is not automatically added by kalman filter library
    # todo check if above is correct
    # state variables
    I_eff = state[0]
    G_s = state[1]
    R_a = state[2]
    R_a_neg_1 = state[3]
    p_1 = state[4]
    p_2 = state[5]
    p_4 = state[6]
    tau = state[7]

    # other required variables not part of the state
    # technically they should have been part of the state as per equation [7] but since the paper
    # doesn't do that, we don't make it part of the state. To add noise, we will just do it here it But
    # the more correct thing would be if it was part of the state and noise was added in the previous transition.
    # todo check if above is correct
    w_k = np.random.normal(1)

    I_p = 0 + w_k
    C = 0 + w_k
    p_3 = 0 + w_k
    V = 0 + w_k # todo try a constant value like 140 that prof. mentioned
    # todo check for nonzero for V

    # compute I_eff(k+1)
    component_1 = h * (p_2 * (I_eff/(h * p_2) - I_eff))
    component_2 = p_3 * I_p
    I_eff_next = component_1 + component_2

    # compute R_a(k+1)
    a = np.exp((h/tau))
    component_1 = (h * C) / (V * a * tau)
    component_2 = (2 * R_a) / a
    component_3 = R_a_neg_1 / a ** 2
    R_a_next = component_1 + component_2 - component_3

    # assuming G_b to be static for now todo have asked the prof whether this is fine.
    # otherwise the transition function will be time-dependent and that's way harder to implement.
    G_b = 100

    # computing G_s(k+1)
    component_1 = p_1 * (G_b + (G_s / (h * p_1)) - G_s)
    component_2 = p_2 * I_eff * G_s
    component_3 = R_a
    G_s_next = h * (component_1 - component_2 + component_3)

    # remaining variables for the next state
    R_a_neg_1_next = R_a
    p_1_next = p_1
    p_2_next = p_2
    p_4_next = p_4
    tau_next = tau

    next_state = [
        I_eff_next,
        G_s_next,
        R_a_next,
        R_a_neg_1_next,
        p_1_next,
        p_2_next,
        p_4_next,
        tau_next
    ]
    next_state = next_state + noise
    return next_state


def observation_function(state, noise):
    # the observation function takes the state and returns the CGM value only because that's what we
    # actually measure
    G_s = state[1]
    return G_s + noise


if __name__ == "__main__":
    cgm_to_meal = pd.read_csv('data/cgm_to_meal.csv')
    cgm_to_meal = cgm_to_meal.dropna()
    cgm = cgm_to_meal['cgm'].to_numpy()

    TRAIN_POINTS = 50
    cgm = cgm[:TRAIN_POINTS]

    # kalman filter inputs
    # transition_covariance = np.diag([1e-06, 1e-06, 1e-03, 1e-03, 1e-02, 1e-01, 1e-02, 1e-01])
    transition_covariance = np.eye(8)
    observation_covariance = 100
    initial_state_mean = [0, cgm[0], 0, 0, 0.068, 0.037, 1.3, 20]
    initial_state_covariance = np.eye(8)

    # sample from model
    kf = UnscentedKalmanFilter(
        transition_function, observation_function,
        transition_covariance, observation_covariance,
        initial_state_mean, initial_state_covariance
    )

    # filtered_state_estimates = kf.filter(cgm)[0]
    smoothed_state_estimates = kf.smooth(cgm)[0]

