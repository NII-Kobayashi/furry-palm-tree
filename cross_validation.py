# Author: Niharika Singhal
#
# For license information, see LICENSE.txt

"""
Function for checking the accuracy of the model based on k-Fold cross-validation

References
----------
.. *Kobayashi and Lambiotte, ICWSM, pp. 191-200, 2016; Zhao et al., KDD, pp. 1513-1522, 2015*.
"""

from sklearn.model_selection import KFold
import statistics
from estimate import *
from prediction import *


def cross_validation_error(k_fold, event_list_data, max_value_itr):
    """
    evaluate the mean and median of the errors, and their correlations
    :param k_fold: k_fold cross-validation
    :param event_list_data: list, containing the cumulative number of followers at an observation time, the number of
    followers of the tweeted person, and the total number of retweets at an observation time and at prediction times
    :param max_value_itr: the number of windows used for prediction
    :return: the mean and median of the errors and their correlations
    """
    est_list_all = []
    actual_list_all = []
    error_list_all = []
    correlation_list = []
    kf = KFold(n_splits=k_fold)
    for train_index, test_index in kf.split(event_list_data):
        original_followers = [(event_list_data[i][0]) for i in range(len(event_list_data))]
        total_follower = [(event_list_data[i][1]) for i in range(len(event_list_data))]
        event_t = [(event_list_data[i][2]) for i in range(len(event_list_data))]
        event_pred_actual_log = [(event_list_data[i][3]) for i in range(len(event_list_data))]
        event_pred_actual = [(event_list_data[i][4]) for i in range(len(event_list_data))]

        original_followers_arr = np.asarray(original_followers)
        total_follower_arr = np.asarray(total_follower)
        event_t_arr = np.asarray(event_t)
        event_pred_actual_arr_log = np.asarray(event_pred_actual_log)
        event_pred_actual_arr = np.asarray(event_pred_actual)

        train_original_foll, test_original_foll = original_followers_arr[train_index], original_followers_arr[
            test_index]
        train_tot_foll, test_tot_foll = total_follower_arr[train_index], total_follower_arr[test_index]
        train_event_t, test_event_t = event_t_arr[train_index], event_t_arr[test_index]
        train_event_pred_act_log, test_event_pred_act_log = \
            event_pred_actual_arr_log[train_index], event_pred_actual_arr_log[test_index]
        train_event_pred_act, test_event_pred_act = event_pred_actual_arr[train_index], event_pred_actual_arr[
            test_index]

        # estimation
        parameters_estimated = parameter_estimation_lr_n(train_original_foll, train_tot_foll, train_event_t,
                                                         train_event_pred_act_log)

        # prediction

        est_rf_list = [prediction_lr_n(parameters_estimated, test_event_t[i], test_tot_foll[i], test_original_foll[i])
                       for i in range(len(test_event_t))]

        # Error estimation and correlation
        for i in range(len(est_rf_list)):
            value_estimated = est_rf_list[i]
            value_actual = test_event_pred_act[i]
            est_list = []
            actual_list = []
            s_xy_list = []
            s_x_list = []
            s_y_list = []
            correlation_val = 0
            for j in range(max_value_itr):
                if j == 0:
                    est_value = value_estimated[0] - math.exp(test_event_t[i])
                    actual_value = value_actual[0] - math.exp(test_event_t[i])
                    s_x = actual_value * actual_value
                    s_y = est_value * est_value
                    s_xy = actual_value * est_value
                else:
                    est_value = value_estimated[j] - value_estimated[j - 1]
                    actual_value = value_actual[j] - value_actual[j - 1]
                    s_x = actual_value * actual_value
                    s_y = est_value * est_value
                    s_xy = actual_value * est_value
                est_list.append(est_value)
                actual_list.append(actual_value)
                s_xy_list.append(s_xy)
                s_x_list.append(s_x)
                s_y_list.append(s_y)
            est_list_all.append(est_list)
            actual_list_all.append(actual_list)
            error_list = [abs(actual_list[j] - est_list[j]) for j in range(len(est_list))]  # error for one file
            error_list_all.append(sum(error_list))
            if sum(s_x_list) > 0 and sum(s_y_list) > 0:
                correlation_val = sum(s_xy_list) / math.sqrt(sum(s_x_list) * sum(s_y_list))
            if sum(s_x_list) > 0 and sum(s_y_list) == 0:
                correlation_val = 0
            if sum(s_x_list) == 0 and sum(s_y_list) > 0:
                correlation_val = 0
            if sum(s_x_list) == 0 and sum(s_y_list) == 0:
                correlation_val = 1
            correlation_list.append(correlation_val)

    med = statistics.median(error_list_all)
    mea = statistics.mean(error_list_all)
    med_cor = statistics.median(correlation_list)
    mea_cor = statistics.mean(correlation_list)
    return med, mea, med_cor, mea_cor
