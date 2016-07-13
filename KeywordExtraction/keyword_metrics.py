__author__ = 'tangy'


"""
P/R : http://research.ijcaonline.org/volume61/number1/pxc3884445.pdf
"""

def keyword_prf(y_true,y_pred):
    total_precision = 0.0
    total_recall = 0.0
    for keywords_true,keywords_pred in zip(y_true,y_pred):
        keywords_true_set = set(keywords_true)
        keywords_pred_set = set(keywords_pred)
        # True-Positive => "True" indicates predicted as keywords
        # "Positives" indicates predicted are actually keywords
        # keywords which actually exist and are correctly predicted
        true_positives_count = len(keywords_true_set.intersection(keywords_pred_set))
        # False Negatives => Which we predicted as actually not keywords but actually are keywords
        # keywords which actually exist but are not detected by the algorithm
        false_negatives_count = len(keywords_true_set) - true_positives_count
        # False Positives =>
        # Indicates which we predicted as positives(actual keywords) but are actually not
        # keywords which are extracted by the algo but not actual keywords
        false_positives_count = len(keywords_pred_set) - true_positives_count
        # P/R/F Calculation
        # precision = TP/(TP+FP) -> predicted and actually keywords/total predicted keywords
        total_precision += (true_positives_count/float(true_positives_count + false_positives_count))
        # total_precision += (true_positives_count/float(len(keywords_pred)))
        # recall = TP/(TP + FN) -> predicted and actually keywords/total actual keywords
        total_recall += true_positives_count/float(true_positives_count + false_negatives_count)
        # total_recall += true_positives_count/float(len(keywords_true))
    avg_precision = total_precision*100/round(len(y_true),2)
    avg_recall = total_recall*100/round(len(y_true),2)
    if avg_precision != 0 and avg_recall != 0:
        avg_fscore = 2*avg_precision*avg_recall/(avg_precision + avg_recall)
    else:
        avg_fscore = 0
    return avg_precision,avg_recall,avg_fscore

def keyword_prf_onegram(y_true,y_pred):
    def onegram(keyword_lst):
        onegrams = []
        for keyword in keyword_lst:
            onegrams += keyword.split(" ")
        return onegrams
    true_positives_count = 0
    false_negatives_count = 0
    false_positives_count = 0
    for keywords_true,keywords_pred in zip(y_true,y_pred):
        keywords_true_set = set(onegram(keywords_true))
        keywords_pred_set = set(onegram(keywords_pred))
        # True-Positive => "True" indicates predicted as keywords
        # "Positives" indicates predicted are actually keywords
        # keywords which actually exist and are correctly predicted
        true_positives_count_iter = len(keywords_true_set.intersection(keywords_pred_set))
        true_positives_count += true_positives_count_iter
        # False Negatives => Which we predicted as actually not keywords but actually are keywords
        # keywords which actually exist but are not detected by the algorithm
        false_negatives_count += len(keywords_true_set) - true_positives_count_iter
        # False Positives =>
        # Indicates which we predicted as positives(actual keywords) but are actually not
        # keywords which are extracted by the algo but not actual keywords
        false_positives_count += len(keywords_pred_set) - true_positives_count_iter
    # precision = TP/(TP+FP) -> predicted and actually keywords/total predicted keywords
    precision = true_positives_count/float(true_positives_count + false_positives_count)
    # recall = TP/(TP + FN) -> predicted and actually keywords/total actual keywords
    recall = true_positives_count/float(true_positives_count + false_negatives_count)
    if precision != 0 and recall != 0:
        fscore = 2*precision*recall/(precision + recall)
    else:
        fscore = 0
    return precision,recall,fscore

