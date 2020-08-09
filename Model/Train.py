import pickle
import numpy as np
import tensorflow as tf
from collections import Counter
from Model.BiLSTM_CRF import BiLSTM_CRF, train_one_step, predict, calculate_metrics, extract_label
from Model.Preprocess import convert_data, format_data, load_char_embeddings

def traing_BiLSTM_CRF():
    EMBED_DIM = 50
    HIDDEN_DIM = 32
    EPOCH = 20
    LEARNING_RATE = 0.01

    char_embed_dict = load_char_embeddings("../Data/vec.txt")
    with open ("../Data/weiboNER_2nd_conll.train.pkl", "rb") as file_test:
        tag_dic_t = pickle.load(file_test)
        char_dic_t = pickle.load(file_test)
        word_dic_t = pickle.load(file_test)
        sentence_list_t = pickle.load(file_test)
        tags_t = pickle.load(file_test)
        data_test = pickle.load(file_test)
        label_test = pickle.load(file_test)
    length = len(data_test)

    with open ("../Data/weiboNER_Corpus.train.pkl", "rb") as file_train:
        tag_dic = pickle.load(file_train)
        char_dic = pickle.load(file_train)
        word_dic = pickle.load(file_train)
        sentence_list = pickle.load(file_train)
        tags = pickle.load(file_train)
        data_train = pickle.load(file_train)
        label_train = pickle.load(file_train)

    data_duplicate = data_train[length:]
    label_duplicate = label_train[length:]

    # Oversampling the named entities.
    for i in range(3):
        data_train.extend(data_duplicate)
        label_train.extend(label_duplicate)
    # print(len(data_train))
    # Undersampling the data without named entities.
    for i in range(length):
        label = label_train[i]
        # for l in label:
        #     if label
        dic = Counter(label)
        # print(dic, "\t", len(label))
        if dic[16] == len(label):
            del label_train[i]
            del data_train[i]

    data_train, label_train = format_data(data_train, label_train)
    vocab_size = len(char_dic)
    tag_size = len(tag_dic)

    train_dataset = tf.data.Dataset.from_tensor_slices((data_train, label_train))
    train_dataset = train_dataset.shuffle(len(data_train)).batch(128, drop_remainder=True)

    model = BiLSTM_CRF(HIDDEN_DIM, vocab_size, tag_size, EMBED_DIM)
    optimizer = tf.keras.optimizers.Adam(LEARNING_RATE)

    # gold_labels = []
    for e in range(EPOCH):
        for i, (data_batch, label_batch) in enumerate(train_dataset):
            # step += 1
            loss, logits, text_lens = train_one_step(model, data_batch, label_batch, optimizer)
            # if e == 19:
                # real_labels = extract_label(text_lens, label_batch)
                # gold_labels.extend(real_labels)

            if (i + 1) % 5 == 0:
                print("Epoch:", e, " Loss:", loss.numpy())

    # pred_labels = []
    # gold_labels = []
    # for i, (data, label) in enumerate(train_dataset):
    #     # print(np.array(label).shape)
    #     gold_labels.extend(np.array(label))
    #     predictions = predict(model, label, data)
    #     # print(len(predictions))
    #     pred_labels.extend(predictions)
    #
    # # 为了解决实际标签和预测标签不一致的问题，该问题由随机排序导致
    # for s in range(len(pred_labels)):
    #     pred_len = len(pred_labels[s])
    #     gold_label = gold_labels[s]
    #     effective_part = gold_label[:pred_len]
    #     gold_labels[s] = effective_part

    # for i in range(len(pred_labels)):
    #     print(i, "Pred len: ", len(pred_labels[i]), "Gold len: ", (len(gold_labels[i])))
    # print(len(gold_labels))

    # with open("labels2.pkl", "wb") as file:
    #     pickle.dump(pred_labels, file)
    #     pickle.dump(gold_labels, file)

    # with open ("../Data/weiboNER_2nd_conll.train.pkl", "rb") as file_test:
    #     tag_dic_t = pickle.load(file_test)
    #     char_dic_t = pickle.load(file_test)
    #     word_dic_t = pickle.load(file_test)
    #     sentence_list_t = pickle.load(file_test)
    #     tags_t = pickle.load(file_test)
    #     data_test = pickle.load(file_test)
    #     label_test = pickle.load(file_test)
    # data_test, label_test = format_data(data_test, label_test)
    # vocab_size_t = len(char_dic_t)
    # tag_size_t = len(tag_dic_t)

    # test_dataset = tf.data.Dataset.from_tensor_slices((data_test, label_test))
    # test_dataset = test_dataset.shuffle(len(data_test)).batch(64, drop_remainder=True)


    with open ("../Data/weiboNER_2nd_conll.test.pkl", "rb") as file_test:
        tag_dic_test = pickle.load(file_test)
        char_dic_test = pickle.load(file_test)
        word_dic_test = pickle.load(file_test)
        sentence_list_test = pickle.load(file_test)
        tags_test = pickle.load(file_test)
        data_test = pickle.load(file_test)
        label_test = pickle.load(file_test)
    data_test_t, label_test_t = format_data(data_test, label_test)
    vocab_size_test = len(char_dic_test)
    tag_size_test = len(tag_dic_test)
    test_dataset = tf.data.Dataset.from_tensor_slices((data_test, label_test))
    test_dataset = test_dataset.shuffle(len(data_test_t)).batch(64, drop_remainder=True)

    gold_labels_test = []
    pred_labels_test = []

    for i, (data_test, label_test) in enumerate(test_dataset):
        # print(np.array(label).shape)
        gold_labels_test.extend(np.array(label_test))
        predictions_test = predict(model, label_test, data_test)
        # print(len(predictions))
        pred_labels_test.extend(predictions_test)


    with open("labels_test.pkl", "wb") as file:
        pickle.dump(pred_labels_test, file)
        pickle.dump(gold_labels_test, file)


if __name__ == "__main__":
    traing_BiLSTM_CRF()

    # p = [[16, 16, 7, 15, 16, 16, 2, 8],
    #      [16, 16, 16, 5, 8, 16, 16, 16]]
    # l = [[16, 7, 15, 16, 16, 16, 2, 8],
    #      [16, 16, 16, 5, 8, 16, 8, 6]]
    # precision, recall, f1 = calculate_metrics(p, l)
    # print(precision, "\t", recall, "\t", f1)