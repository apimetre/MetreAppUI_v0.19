
import json
import numpy as np
import datetime as datetime
import time
import math

def process(data_dict, dt_, debug):
    
    def running_mean(x, N):
        cumsum = np.cumsum(np.insert(x, 0, 0))
        return (cumsum[N:] - cumsum[:-N]) / float(N)
    trigger_ix = data_dict['trigger_index']
    sample_rate = data_dict['SAMPLES_PER_SEC']
    

    
    sample_rate = 250
    # Define baseline window in seconds
    baseline_window = 5
           
    try:
           conversion_factor = float(data_dict['ADS_1115_SCALAR'])
    except:
           conversion_factor = 0.0078125       

    
    # Change data to mV
    all_signal = np.array(data_dict['data']) * conversion_factor
    #print(all_signal)
    
    # Fix any gaps in data due to error logging
    errs = data_dict['log_errors']
    if len(errs) >0:
        for err in errs:
            err_left = all_signal[int(err) - 1]
            err_right = all_signal[int(err) + 1]
            err_replacement = (err_left + err_right)/2
            all_signal[err] = err_replacement
    
    
    # Get all of the pre-signal data
    pre_signal_data = all_signal[:trigger_ix]
    
    
    # Get the baseline_window seconds of data just before the sample was taken
    baseline_data = pre_signal_data[-(sample_rate * baseline_window):]
    

    # Get the mean of the baseline data to calculate the new baseline
    baseline = np.mean(baseline_data)
    
    # Save baseline value
    data_dict['baseline'] = float(baseline)
    
    # filter the data with a rolling mean proportional to the sample_rate
    # rolling mean filter window in seconds
    window = .1 #seconds
    
    filter_samples = sample_rate * window
    
    rolling_mean_all = running_mean(all_signal, int(filter_samples)) - baseline
    
    
    data_dict['Data_pts'] = int(len(rolling_mean_all))

    # Update trigger index to adjust for rolling mean truncation
    trigger_adjusted = math.floor(trigger_ix - filter_samples/2)
    
    # Get the signal data from t=0
    signal_data = rolling_mean_all[trigger_adjusted:]
    
    
    # Truncate the signal data for the ML model
    signal_data_for_ML = signal_data[:7500].tolist()
    
    data_dict['mV_rolling_mean'] = signal_data_for_ML
    
    # PROCESS TEST
    
    peak_pos = np.amax(signal_data)
    peak_pos_t_ix = np.argmax(signal_data)
    peak_pos_t = peak_pos_t_ix/sample_rate

    peak_neg = np.amin(signal_data)
    peak_neg_t_ix = np.argmin(signal_data)
    peak_neg_t = peak_neg_t_ix/sample_rate
    
    data_dict['Peak_pos'] = float(peak_pos)
    data_dict['Peak_pos_t'] = float(peak_pos_t)
    data_dict['Peak_pos_t_ix'] = float(peak_pos_t_ix)
    
    data_dict['Peak_neg'] = float(peak_neg)
    data_dict['Peak_neg_t'] = float(peak_neg_t)
    data_dict['Peak_neg_t_ix'] = float(peak_neg_t_ix)
    
    pos_data_mV = signal_data[peak_neg_t_ix:]
    if debug:
        print('neg peak ix', peak_neg_t_ix)
        print('length of pos data mv', len(pos_data_mV))
    try:
        cross_t_ix = np.amin(np.where(pos_data_mV >= 0))
        cross_t = peak_neg_t + cross_t_ix/sample_rate
        test_type = 'okay'
    except:    
        cross_t_ix = 0
        cross_t = 0
        test_type = 'air_blank'
    data_dict['Cross_t'] = float(cross_t)
    data_dict['Cross_t_ix'] = float(cross_t_ix)
    data_dict['Test_Type'] = str(test_type)
    

    # Calculate Positive Area
    
    pos_data_mV = pos_data_mV[cross_t_ix:]  # test_data.truncate(before=cross_t_ix)
    
    pk_8th = peak_pos / 8
    pk_16th = peak_pos / 16
    
    tail_data = signal_data[peak_pos_t_ix:]
    last_pt = pos_data_mV[-1]
    
    if last_pt < pk_16th:
        pk_16th_t_ix = np.amax(np.where(tail_data <= pk_16th))
        pos_data_16 = pos_data_mV[:pk_16th_t_ix]
        area_pos_16 = int(np.sum(pos_data_16))
        data_dict['Area_pos_16'] = int(area_pos_16/sample_rate)
    # Exclude these calculations for short tests
    if last_pt < pk_8th:
        pk_8th_t_ix = np.amax(np.where(tail_data <= pk_8th))
        pos_data_8 = pos_data_mV[:pk_8th_t_ix]
        area_pos_8 = int(np.sum(pos_data_8))
        data_dict['Area_pos_8'] = int(area_pos_8/sample_rate)
        area_pos = int(area_pos_8 / sample_rate) * 1.27 - 173
        data_dict['Area_pos'] = float(area_pos)
    else:
        area_pos = 0
        data_dict['Area_pos'] = area_pos
        
    # Calculate Negative Area
    neg_data = signal_data[:cross_t_ix]
    area_neg = np.sum(neg_data)
    data_dict['Area_neg'] = int(area_neg/sample_rate)
    # Calculate Total Area
    data_dict['Area_total'] = int(area_neg/sample_rate + area_pos)
    
    return data_dict
    

