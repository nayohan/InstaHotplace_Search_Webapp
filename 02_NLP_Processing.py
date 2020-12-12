from konlpy.tag import Okt

print("-----------------------------------------------------")
okt = Okt()
sentence = ["말차 좋아하는 사람들이 환장할 카페!!🤍 나도 말차 좋아하는 편이라 이 카페에 기대감이 높았는데 비주얼만큼이나 맛도 최강 ..! 어떻게 저렇게 귀엽게 만드시는지 .. 너무 귀여워서 먹기 아까울정도다! 단점이라하면 양이 조금 적다는거? .. 그 점만 빼면 완전 내 최애 카페가 될 느낌이다 나중에 또 가야즹 ㅎㅎ ~😋"],
            "° 샤로수길 '데일리오아시스'맛 ⭐️⭐️⭐️⭐️분위기 ⭐️⭐️⭐️✔️데일리오아시스(말차쉐이크)✔️말차레몬에이드 돌아다니다가 이뻐보여서 들어간 카페에서 진짜 맛있는 말차쉐이크를 만났어요😭💗일단 쉐이크 위에 올라간 쿠키가 버터향이진~ 한게 쉐이크랑 찰떡궁합🤤 저는 평소 말차를 좋아해서 이곳저곳에서 자주 먹어보는데 여기는 진하면서도 부드러운게 진짜 맛있더라구요! 메뉴도 말차메뉴가 많은걸보니 말차를 밀고있는 카페같았어요ㅎㅎ 🍋🍋사실 말차레몬에이드를 더욱 기대했는데 레몬에이드의 맛이 너무 강했어요 ㅠ 레몬의 맛을 줄이고 말차특유의 쌉싸름한 맛이 더 나면 좋을거같아요!! 사실 말차 맛이 정말 미미하게 낫다능 ㅠㅠ 말차레몬에이드라고 해서 너무너무 기대가 커서 그렇지 달달하고 쌍콤하니 맛은 있었어요! 디저트류로 티라미수랑 수플레팬케이크가 있더라구요! 너무 배불러서 이번엔 못먹었지만 조만간 재방문해서 디저트도 뿌셔볼게요🙋🏻‍♀️🙋🏻‍♀️1층이 창도 넓고 트여있어서 분위기가 아주 좋았어요! 가시게되면 1층 추천드려용❣️"]
# print(okt.morphs(sentence))
# print(okt.nouns(sentence))
# print(okt.pos(sentence))

#형태소 분석
print("-----------------------------------------------------")
def text_preprocessing(text_list):
    stopwords = ['을', '를', '이', '가', '은', '는', 'null'] #불용어 설정
    tokenizer = Okt() #형태소 분석기 
    token_list = []
    for text in text_list:
        token = tokenizer.morphs(text) #형태소 분석
        token = [t for t in token if t not in stopwords or type(t) != float] #형태소 분석 결과 중 stopwords에 해당하지 않는 것만 추출
        token_list.append(token)
    return token_list, tokenizer #형태소 분석기를 따로 저장한 이유는 후에 test 데이터 전처리를 진행할 때 이용
new_sentence, okt = text_preprocessing(sentence) 
print(new_sentence)


#Vectorization
print("-----------------------------------------------------")
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
def text2sequence(train_text, max_len=100):
    tokenizer = Tokenizer() #keras의 vectorizing 함수 호출
    tokenizer.fit_on_texts(train_text) #train 문장에 fit
    print(tokenizer.word_index)
    train_X_seq = tokenizer.texts_to_sequences(train_text) #각 토큰들에 정수 부여
    print(train_X_seq)
    vocab_size = len(tokenizer.word_index) + 1 #모델에 알려줄 vocabulary의 크기 계산
    print('vocab_size : ', vocab_size)
    X_train = pad_sequences(train_X_seq, maxlen = max_len) #설정한 문장의 최대 길이만큼 padding
    return X_train, vocab_size, tokenizer

train_X, vocab_size, vectorizer = text2sequence(new_sentence, max_len = 100)
print(train_X)
print(train_X.shape, vocab_size)
print(vectorizer)
print(train_X.dtype)


#Embbedding
print("-----------------------------------------------------")
import gensim
import numpy as np
word2vec = gensim.models.KeyedVectors.load_word2vec_format('./NLP/GoogleNews-vectors-negative300.bin.gz', binary = True)
embedding_matrix = np.zeros((vocab_size, 300)) #300차원의 임베딩 매트릭스 생성

for index, word in enumerate(new_sentence[0]): #vocabulary에 있는 토큰들을 하나씩 넘겨줍니다.
    print(index, word)    
    if word in word2vec: #넘겨 받은 토큰이 word2vec에 존재하면(이미 훈련이 된 토큰이라는 뜻)
        embedding_vector = word2vec[word] #해당 토큰에 해당하는 vector를 불러오고
        embedding_matrix[index] = embedding_vector #해당 위치의 embedding_mxtrix에 저장합니다.
    else:
        print("word2vec에 없는 단어입니다.")
        # break
print(embedding_matrix)
print(embedding_matrix.shape)

#Modeling
import keras
from keras import models
from keras import layers
def LSTM(vocab_size=145, max_len=1000):
    model = keras.Sequential()
    model.add(layers.Embedding(vocab_size, 300,weights = [embedding_matrix], input_length = max_len)) #임베딩 가중치 적용 코드
    model.add(layers.SpatialDropout1D(0.3))
    model.add(LSTM(145))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(64, activation='relu', kernel_regularizer = keras.regularizers.l2(0.001)))
    model.add(layers.Dense(1, activation='sigmoid'))
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics='accuracy')
    model.summary()
    return model

LSTM(vocab_size)
