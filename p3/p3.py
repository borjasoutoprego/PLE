"""
@authors: Nina López Laudenbach (nina.laudenbach), Borja Souto Prego (borja.souto)
"""

from sklearn import preprocessing
import numpy as np
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Input, Embedding, Flatten, Dense, LSTM, TimeDistributed, Bidirectional
from nervaluate import Evaluator
from keras.utils import to_categorical
from tensorflow.keras.preprocessing.sequence import pad_sequences
import sys

model_type = str(sys.argv[1])
task = str(sys.argv[2])
train_path = str(sys.argv[3])
dev_path = str(sys.argv[4])
test_path = str(sys.argv[5])
batch_size = int(sys.argv[6])
epochs = int(sys.argv[7])

class txtReader:
    """Reads a txt file and returns a list of lists with the words and a list of lists with the ids of the words"""
    def __init__(self, filename):
        self.filename = filename

    def read_split(self):
        with open(self.filename, 'r') as f:
            file_read = f.read()
        lines = file_read.split('\n')
        text = []
        text_id = []
        tmp = []
        tmp_id = []
        for i in lines:
            if i == '':
                if len(tmp) != 0:
                    text.append(tmp)
                    text_id.append(tmp_id)
                    tmp = []
                    tmp_id = []
            else:
                word = i.split('\t')
                tmp.append(word[0])
                tmp_id.append(word[1])

        return text, text_id

class alphabet:
    """Creates a dictionary with the words and their ids"""
    def __init__(self, train_file, dev_file, test_file):
        self.train_file = train_file
        self.dev_file = dev_file
        self.test_file = test_file
        self.data = dict()
        self.labels = dict()

    def read_split(self):
        """Reads the files and returns a list of lists with the words and a list of lists with the ids of the words"""
        text_files = []
        for text_file in [self.train_file, self.dev_file, self.test_file]:
            txt = txtReader(text_file)
            text, text_id = txt.read_split()
            text_files.append(text)
            text_files.append(text_id)

        return text_files[0], text_files[1], text_files[2], text_files[3], text_files[4], text_files[5]
    
    def _tagger(self, dataset, cnt, dictionary):
        """Creates a dictionary with the words and their ids"""
        for i in dataset: # i es una frase
            for j in i: # j es una palabra
                pos = i.index(j) # pos es la posicion de la palabra en la frase
                if j not in dictionary:
                    dictionary[j] = cnt
                    i[pos] = cnt
                    cnt += 1
                else:
                    i[pos] = dictionary[j]

        return dataset, cnt, dictionary 

    def labelEncoder(self):
        """Creates a dictionary with the labels and their ids"""
        train, train_id, dev, dev_id, test, test_id = self.read_split()
        cnt = 1
        cnt_id = 0

        train, cnt, self.data = self._tagger(train, cnt, self.data) 
        train_id, cnt_id, self.labels = self._tagger(train_id, cnt_id, self.labels)
        dev, cnt, self.data = self._tagger(dev, cnt, self.data)
        dev_id, cnt_id, self.labels = self._tagger(dev_id, cnt_id, self.labels)
        
        len_train = 0
        for i in train:
            len_train += len(i)

        for phrase_te in test:
            for te in phrase_te:
                pos = phrase_te.index(te)
                if te not in self.data:
                    self.data[te] = len_train
                    phrase_te[pos] = self.data[te]
                else:
                    phrase_te[pos] = self.data[te]

        for phrase_te_id in test_id:
            for te_id in phrase_te_id:
                pos_id = phrase_te_id.index(te_id)
                if te_id not in self.labels:
                    self.labels[te_id] = len_train
                    phrase_te_id[pos_id] = self.labels[te_id]
                else:
                    phrase_te_id[pos_id] = self.labels[te_id] 

        return train, train_id, dev, dev_id, test, test_id, self.data, self.labels

class FFTagger():
    """Class that implements a Feed Fordward tagger"""
    def __init__(self, train, train_id, dev, dev_id, test, test_id, labels_dict, n, loss, optimizer, metrics, batch_size, epochs): 
        self.model = Sequential()
        self.train = train
        self.train_id = train_id
        self.dev = dev
        self.dev_id = dev_id
        self.test = test
        self.test_id = test_id
        self.labels_dict = labels_dict
        self.n = n
        len_train = 0
        for i in train:
            len_train += len(i)
        self.vocab_size = len_train + 1 # +1 por valores desconocidos en test
        self.classes = labels_dict.keys()
        self.num_classes = len(labels_dict)
        self.loss = loss
        self.optimizer = optimizer
        self.metrics = metrics
        self.train_windows = []
        self.dev_windows = []
        self.test_windows = []
        self.batch_size = batch_size
        self.epochs = epochs

    def build_model(self): 
        """Builds the model"""
        self.model.add(Input(shape=(self.n*2+1,), dtype=tf.int32))
        self.model.add(Embedding(input_dim = self.vocab_size, output_dim=20, mask_zero=True, input_length=self.n*2+1))
        self.model.add(Flatten())
        self.model.add(Dense(64, activation='relu'))
        self.model.add(Dense(self.num_classes, activation='softmax'))

    def train_model(self):
        """Trains the model"""
        # Añadimos padding a las frases y las dividimos en ventanas de tamaño 2n+1
        padding = []
        for i in range(self.n):
            padding.append(0)

        padded_train = []
        padded_dev = []
        one_hot_train_id = []
        one_hot_dev_id = []
        for j in range(len(self.train)):
            padded_phrase = padding + self.train[j] + padding
            padded_train.append(padded_phrase) # padding
            for w in range(self.n, len(padded_phrase)-self.n): # división en ventanas
                self.train_windows.append(padded_phrase[w-self.n:w+self.n+1])
            one_hot_phrase = to_categorical(self.train_id[j], num_classes=self.num_classes) # one-hot encoding
            for v in one_hot_phrase:
                one_hot_train_id.append(v)

        for k in range(len(self.dev)):
            padded_phrase_dev = padding + self.dev[k] + padding
            padded_dev.append(padded_phrase_dev)
            for w in range(self.n, len(padded_phrase_dev)-self.n):
                self.dev_windows.append(padded_phrase_dev[w-self.n:w+self.n+1])
            one_hot_phrase_dev = to_categorical(self.dev_id[k], num_classes=self.num_classes)
            for v in one_hot_phrase_dev:
                one_hot_dev_id.append(v)
        
        # Convertimos las listas en tensores
        train_tensor = tf.data.Dataset.from_tensor_slices((self.train_windows, one_hot_train_id))
        train_tensor = train_tensor.batch(self.batch_size)
        dev_tensor = tf.data.Dataset.from_tensor_slices((self.dev_windows, one_hot_dev_id))
        dev_tensor = dev_tensor.batch(self.batch_size)

        # Reescribimos las variables globales
        self.train = padded_train
        self.dev = padded_dev

        self.model.compile(loss=self.loss, optimizer=self.optimizer, metrics=self.metrics)
        self.model.fit(train_tensor, epochs=self.epochs, validation_data=dev_tensor, verbose=1)

    def evaluate_model(self, task):
        """Evaluates the model"""
        padding = []
        for i in range(self.n):
            padding.append(0)
        
        # Añadimos el padding, dividimos en ventanas y hacemos one-hot encoding de las etiquetas
        padded_test = []
        one_hot_test_id = []
        for j in range(len(self.test)):
            padded_phrase_test = padding + self.test[j] + padding
            padded_test.append(padded_phrase_test)
            for w in range(self.n, len(padded_phrase_test)-self.n): # división en ventanas
                self.test_windows.append(padded_phrase_test[w-self.n:w+self.n+1])
            one_hot_phrase_test = to_categorical(self.test_id[j], num_classes=self.num_classes) # one-hot encoding
            for v in one_hot_phrase_test:
                one_hot_test_id.append(v)

        test_labels = [] # guarda las etiquetas como cadena de caracteres
        test_labels_length = [] # guarda la longitud de las oraciones
        for i in self.test_id: 
            temp_phrase = []
            for j in i: 
                for k, v in self.labels_dict.items():
                    if j == v:
                        temp_phrase.append(k)
            test_labels.append(temp_phrase)
            test_labels_length.append(len(temp_phrase))

        test_tensor = tf.data.Dataset.from_tensor_slices((self.test_windows, one_hot_test_id))
        test_tensor = test_tensor.batch(self.batch_size)
        
        if task == "PoS":
            loss, accuracy = self.model.evaluate(test_tensor, verbose=1)
            print("Loss: ", loss, '\nAccuracy: ', accuracy)
            # return loss, accuracy
        elif task == "NER":
            loss, accuracy = self.model.evaluate(test_tensor, verbose=1)
            pred = self.model.predict(test_tensor).astype(np.float32)

            # para cada elemento de pred obtenemos la etiqueta numérica  
            predictions = np.argmax(pred, axis=-1)
            
            # convertimos las etiquetas numéricas a etiquetas de texto
            pred_labels = []
            test_index = 0
            tmp_phrase = []
            for l in predictions:
                for k, v in self.labels_dict.items():
                    if l == v:
                        tmp_phrase.append(k)
                    if len(tmp_phrase) == test_labels_length[test_index]:
                        pred_labels.append(tmp_phrase)
                        tmp_phrase = []
                        test_index += 1
                        break

            numeric_tags = set()
            for i in self.train_id:
                numeric_tags = set(numeric_tags|set(i))
            for j in self.dev_id:
                numeric_tags = set(numeric_tags|set(j))
            numeric_tags = list(numeric_tags)

            # convertimos las etiquetas numéricas a etiquetas de texto
            tags = []
            for t in numeric_tags:
                for k, v in self.labels_dict.items():
                    if t == v:
                        tags.append(k)

            # Nos quedamos con las etiquetas de la entidad (sin B e I)
            evaluator_tags = []
            for tag in tags:
                if tag == "O":
                    continue
                elif tag == '':
                    continue
                else:
                    evaluator_tag = tag[2:]

                if evaluator_tag not in evaluator_tags:
                    evaluator_tags.append(evaluator_tag)
            
            evaluator = Evaluator(test_labels, pred=pred_labels, tags=evaluator_tags, loader="list")
            results, results_by_tag = evaluator.evaluate()
            
            # return loss, accuracy, results, results_by_tag
            print('Loss: ', loss, '\nAccuracy: ', accuracy, '\nResults: ', results, '\nResults by tag: ', results_by_tag, '\n')

        else:
            return "Task not found"

class LSTMTagger():
    """Class that implements a LSTM tagger"""
    def __init__(self, train, train_id, dev, dev_id, test, test_id, data_dict, labels_dict, loss, optimizer, metrics, batch_size, epochs):
        self.model = Sequential()
        self.train = train
        self.train_id = train_id
        self.dev = dev
        self.dev_id = dev_id
        self.test = test
        self.test_id = test_id
        self.data_dict = data_dict
        self.labels_dict = labels_dict
        len_train = 0
        for i in train:
            len_train += len(i)
        self.vocab_size = len_train + 1
        self.classes = labels_dict.keys()
        self.num_classes = len(labels_dict)
        self.loss=loss
        self.optimizer=optimizer
        self.metrics=metrics
        self.train_windows = []
        self.train_windows_id = []
        self.dev_windows = []
        self.dev_windows_id = []
        self.test_windows = []
        self.test_windows_id = []
        self.maxlen = 0
        self.batch_size = batch_size
        self.epochs = epochs

    def build_model(self, bidirectional=False):
        """Builds the model"""
        self.model.add(Embedding(input_dim=self.vocab_size, output_dim=20, mask_zero=True, input_length=self.maxlen))
        if bidirectional:
            self.model.add(Bidirectional(LSTM(64, return_sequences=True)))
        else:
            self.model.add(LSTM(64, return_sequences=True))
        self.model.add(TimeDistributed(Dense(units=self.num_classes, activation='softmax'))) 

    def _getMaxLength(self, data):
        """Gets the maximum length of the sentences in the dataset"""
        for i in range(len(data)):
            if len(data[i]) > self.maxlen:
                self.maxlen = len(data[i])
        
    def _padder(self, data, data_id):
        """Pads the sentences to the maximum length"""
        padded_data = pad_sequences(data, maxlen=self.maxlen, padding='post')
        padded_data_id = pad_sequences(data_id, maxlen=self.maxlen, padding='post')
        one_hot_data_id = to_categorical(padded_data_id, num_classes=self.num_classes)

        return padded_data, one_hot_data_id

    def preprocessing(self):
        """Pads the sentences to the maximum length and converts the labels to one-hot vectors"""
        self._getMaxLength(self.train)
        self._getMaxLength(self.dev)
        self._getMaxLength(self.test)

        datasets = []
        for data in [[self.train, self.train_id], [self.dev, self.dev_id], [self.test, self.test_id]]:
          padded_data = pad_sequences(data[0], maxlen=self.maxlen, padding='post')
          padded_data_id = pad_sequences(data[1], maxlen=self.maxlen, padding='post')
          one_hot_data_id = to_categorical(padded_data_id, num_classes=self.num_classes)
          datasets.append([padded_data, one_hot_data_id])

        self.train_windows, self.train_windows_id = datasets[0]
        self.dev_windows, self.dev_windows_id = datasets[1]
        self.test_windows, self.test_windows_id = datasets[2]

    def train_model(self):
        """Trains the model"""
        train_tensor = tf.data.Dataset.from_tensor_slices((self.train_windows, self.train_windows_id))
        train_tensor = train_tensor.batch(self.batch_size)
        dev_tensor = tf.data.Dataset.from_tensor_slices((self.dev_windows, self.dev_windows_id))
        dev_tensor = dev_tensor.batch(self.batch_size)

        self.model.compile(loss=self.loss, optimizer=self.optimizer, metrics=self.metrics)
        self.model.fit(train_tensor, epochs=self.epochs, validation_data=dev_tensor)

    def evaluate_model(self, task):
        """Evaluates the model"""
        test_labels = [] # lista que almacena las etiquetas de los elementos de self.test_id
        # Cambiamos las etiquetas de numérico a string
        for i in self.test_id:
            temp_phrase = []
            for j in i:
                for k, v in self.labels_dict.items():
                    if j == v:
                        temp_phrase.append(k)
            test_labels.append(temp_phrase)
        
        lengths = []
        for t in self.test_id:
            lengths.append(len(t))

        test_tensor = tf.data.Dataset.from_tensor_slices((self.test_windows, self.test_windows_id))
        test_tensor = test_tensor.batch(self.batch_size)
        
        if task == "PoS":
            loss, accuracy = self.model.evaluate(test_tensor, verbose=1)
            # return loss, accuracy
            print("Loss: ", loss, '\nAccuracy: ', accuracy)
        elif task == "NER":
            loss, accuracy = self.model.evaluate(test_tensor, verbose=1)
            pred = self.model.predict(test_tensor).astype(np.float32)

            # convertimos las predicciones a etiquetas numéricas
            pred_ids = np.argmax(pred, axis=-1)

            pred_wo_padding = []
            for p in range(len(pred_ids)):
                index = lengths[p]
                pred_wo_padding.append(pred_ids[p][:index])

            # convertimos las etiquetas numéricas a etiquetas de texto
            pred_labels = []
            for l in pred_wo_padding:
                tmp_phrase = []
                for w in l:
                    for k, v in self.labels_dict.items():
                        if w == v:
                            tmp_phrase.append(k)
                pred_labels.append(tmp_phrase)
            
            # obtenemos las etiquetas únicas que hay en el conjunto de train y dev
            numeric_tags = set()
            for i in self.train_id:
                numeric_tags = set(numeric_tags|set(i))
            for j in self.dev_id:
                numeric_tags = set(numeric_tags|set(j))
            numeric_tags = list(numeric_tags)

            # convertimos las etiquetas numéricas a etiquetas de texto
            tags = []
            for t in numeric_tags:
                for k, v in self.labels_dict.items():
                    if t == v:
                        tags.append(k)

            # Nos quedamos con las etiquetas de cada entidad
            evaluator_tags = []
            for tag in tags:
                if tag == "O":
                    continue
                elif tag == '':
                    continue
                else:
                    evaluator_tag = tag[2:]

                if evaluator_tag not in evaluator_tags:
                    evaluator_tags.append(evaluator_tag)

            evaluator = Evaluator(test_labels, pred=pred_labels, tags=evaluator_tags, loader="list")
            results, results_by_tag = evaluator.evaluate()
            
            # return loss, accuracy, results, results_by_tag
            print('Loss: ', loss, '\nAccuracy: ', accuracy, '\nResults: ', results, '\nResults by tag: ', results_by_tag, '\n')
        else:
            return "Task not found"

if __name__=="__main__":

    train, train_id, dev, dev_id, test, test_id, data, labels = alphabet(train_path, dev_path, test_path).labelEncoder()

    if model_type == "ff":
        model = FFTagger(train, train_id, dev, dev_id, test, test_id,  labels, 2, 'categorical_crossentropy', 'adam', ['accuracy'], batch_size, epochs)
        model.build_model()
        model.train_model()
        model.evaluate_model(task)

    elif model_type == "lstm":
        model = LSTMTagger(train, train_id, dev, dev_id, test, test_id, data, labels, 'categorical_crossentropy', 'adam', ['accuracy'], batch_size, epochs)
        model.preprocessing()
        model.build_model(bidirectional=False)
        model.train_model()
        model.evaluate_model(task)

    elif model_type == "bilstm":
        model = LSTMTagger(train, train_id, dev, dev_id, test, test_id, data, labels, 'categorical_crossentropy', 'adam', ['accuracy'], batch_size, epochs) 
        model.preprocessing()
        model.build_model(bidirectional=True)
        model.train_model()
        model.evaluate_model(task)

    else:
        print("Model not found")

