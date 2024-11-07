# ========================================================================
# Wafer map 검사 CNN 모델의 평가 (Confusion matrix)
# 작성일 : 2023-04-03
# ========================================================================
import numpy as np
from sklearn.metrics import (confusion_matrix, accuracy_score,
                             recall_score, precision_score, f1_score)
import matplotlib.pyplot as plt


# confusion matrix 그리는 함수
def plot_confusion_matrix(
        y_pred, y_true, labels,             # 예측값, 실측값, labels = classnames
        title='Confusion Matrix',           # 그래프 제목
        cmap=plt.cm.Blues,                  # plt.cm.get_cmap('Blues') (old version)
        normalize=False,                    # percentage로 표현
        norm_on_model=False):               # 정규화 시 예측값 기준으로 계산

    if normalize:
        if norm_on_model:
            cm = confusion_matrix(y_true, y_pred, normalize='pred')    # ndarray, x축 (y_pred), y축 (y_true)
        else:
            cm = confusion_matrix(y_true, y_pred, normalize='true')    # ndarray, x축 (y_pred), y축 (y_true)
    else:
        cm = confusion_matrix(y_true, y_pred)
    thresh = cm.max() / 2.

    plt.imshow(cm, cmap=cmap)      # interpolation='nearest'
    plt.title(title)
    plt.colorbar()

    con_mat = confusion_matrix(y_true, y_pred)

    ticks = np.arange(len(labels))  # 눈금
    plt.xticks(ticks, labels, rotation=45)
    plt.yticks(ticks, labels, rotation=0, ha='right')         # va : vertical alignment

    if normalize:
        if norm_on_model:  # 모델의 예측값(column)을 기준으로 정규화
            n = con_mat.sum(0)
            for i in range(con_mat.shape[0]):
                for j in range(con_mat.shape[1]):
                    plt.text(j, i, '{:.1f}%'.format(
                        con_mat[i, j] * 100 / n[j]), ha="center", color="w" if cm[i, j] > thresh else "k")
        else:   # 데이터의 참값(row)을 기준으로 정규화
            n = con_mat.sum(1)
            for i in range(con_mat.shape[0]):
                for j in range(con_mat.shape[1]):
                    plt.text(j, i, '{:.1f}%'.format(
                        con_mat[i, j] * 100 / n[i]), ha="center", color="w" if cm[i, j] > thresh else "k")

    else:
        for i in range(con_mat.shape[0]):
            for j in range(con_mat.shape[1]):
                plt.text(j, i, con_mat[i, j], ha="center", va='center', color="w" if cm[i, j] > thresh else "k")

    # plt.tight_layout()
    plt.xlabel('Predicted label', fontsize=12)
    plt.ylabel('Actual label', fontsize=12)
    plt.tight_layout()
    plt.show()


def calculate_cm_metrics(y_pred, y_true):
    # Confusion Matrix 계산
    cm = confusion_matrix(y_true, y_pred)   # 매개변수 순서 : y축, x축

    # 클래스별 TP, FN, FP, TN 값 계산
    n = cm.shape[0]
    precision = np.zeros(n)
    recall = np.zeros(n)
    f1_score = np.zeros(n)
    for i in range(n):
        tp = tp = cm[i, i]
        fn = cm[i].sum() - tp
        fp = cm[:, i].sum() - tp
        tn = cm.sum() - tp - fn - fp

        precision[i] = tp / (tp + fp)
        recall[i] = tp / (tp + fn)
        f1_score[i] = 2 * precision[i] * recall[i] / (precision[i] + recall[i])

    return accuracy_score(y_pred, y_true), precision, recall, f1_score


if __name__ == '__main__':
    # 정답/예측 데이터 생성
    y_true = [2, 0, 2, 2, 0, 1, 1, 2, 2, 0, 1, 2]
    y_pred = [0, 0, 2, 1, 0, 2, 1, 0, 2, 0, 2, 2]

    # 혼동행렬 생성 및 평가지표 계산
    conf_mat = confusion_matrix(y_true, y_pred) # 인자 순서 : y축, x축
    print(conf_mat)

    acc, prc, rcl, f1 = calculate_cm_metrics(y_pred, y_true)
    print('Accuracy = {:.2f}'.format(acc))
    print('Precision = {:.2f}'.format(prc[0]))
    print('Recall = {:.2f}'.format(rcl[0]))
    print('f1-score = {:.2f}'.format(f1[0]))

    # scikit-learn 활용
    print('\nscikit-learn')
    print('Accuracy = {:.2f}'.format(accuracy_score(y_true, y_pred)))
    print('Precision = {:.2f}'.format(precision_score(y_true, y_pred, average=None)[0]))
    print('Recall = {:.2f}'.format(recall_score(y_true, y_pred, average=None)[0]))
    print('F1-score = {:.2f}'.format(f1_score(y_true, y_pred, average=None)[0]))

    # 라벨 설정
    labels = ['center', 'none', 'near-full']
    plot_confusion_matrix(y_pred, y_true, labels, normalize=True, norm_on_model=False)

    """
    y = [1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1]
    _y = [1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1]

    acc, prc, rcl, f1 = calculate_cm_metircs(_y, y)
    print('Accuracy = {:.2f}'.format(acc))
    print('Precision = {:.2f}'.format(prc[0]))
    print('Recall = {:.2f}'.format(rcl[0]))
    print('f1-score = {:.2f}'.format(f1[0]))
    """






