import csv
import cv2
import os
import numpy as np
from keras.callbacks import ModelCheckpoint, EarlyStopping
from keras.models import Model
from keras.layers import BatchNormalization
from keras.layers import Input, Dense, Dropout, Flatten, Convolution2D, MaxPooling2D
from keras.preprocessing.image import ImageDataGenerator
from misc_utils import make_grey

from sklearn.utils import shuffle

def load_dataset():
    """Gets the location of the dataset"""
    
    dataset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset")
    doors_path = os.path.join(dataset_path, "doors")
    not_doors_path = os.path.join(dataset_path, "not_doors")
    
    opencv_doors = []
    is_door = []
    
    def add_folder(folder, is_doors):
        """
        Itrates over a folder and sub folders, and adds the images to the dataset
        """
        for subdir, dirs, files in os.walk(folder):
            for file_name in files:
                full_name = os.path.join(subdir, file_name)
                opencv_doors.append(make_grey(cv2.imread(full_name)))
                is_door.append(is_doors)
        return
    
    add_folder(doors_path, 1)
    add_folder(not_doors_path, 0)
    
    x_tmp, shuffled2 = shuffle(opencv_doors, is_door)
    
    # This takes the opencv images array, and shifts them to the keras model
    x = []
    for i in range(len(x_tmp)):
        x_tmp2 = np.reshape(x_tmp[i], (50, 50, 1))
        x.append(np.transpose(x_tmp2, (2, 0, 1)))
    x = np.array(x)/ 255.0 # Ok, now x is in keras's format, note its transposed and reshaped
    
    
    return x, np.array(shuffled2)

def net(input_shape):
    input_img = Input(input_shape)
    # convolutional layers: (N_kernels, h_kernel, W_kernel)
    conv = BatchNormalization()(input_img)
    conv = Convolution2D(8, 3, 3, activation='relu', border_mode='same')(conv)
    conv = MaxPooling2D((3, 3), strides=(3, 3))(conv)
    # conv = Dropout(0.25)(conv)
    conv = Convolution2D(16, 3, 3, activation='relu', border_mode='same')(conv)
    conv = MaxPooling2D((2, 2), strides=(2, 2))(conv)
    conv = Dropout(0.1)(conv)
    conv = Convolution2D(32, 3, 3, activation='relu', border_mode='same')(conv)
    conv = MaxPooling2D((2, 2), strides=(2, 2))(conv)
    conv = Dropout(0.15)(conv)
    #conv = Convolution2D(32, 3, 3, activation='relu', border_mode='same')(conv)
    #conv = MaxPooling2D((2, 2), strides=(2, 2))(conv)
    #conv = Dropout(0.2)(conv)
    #conv = Convolution2D(32, 3, 3, activation='relu', border_mode='valid')(conv)
    # conv = MaxPooling2D((2, 2), strides=(2, 2))(conv)
    #conv = Dropout(0.25)(conv)
    fc = Flatten()(conv)

    # fully connected layers: (N_newrons)
    # fc = Dense(16, activation='relu')(fc)
    # # fc = Dropout(0.25)(fc)
    fc = Dense(1, activation='sigmoid')(fc)
    model = Model(input=input_img, output=fc)

    return model


def train():
    ###
    # getting dataset from png images:
    
    x, y = load_dataset()

    
    ###
    # neural net trainer:
    model_description = 'model_weights'
    size_batch = len(x)
    epoches_number = 10000
    validation_portion = 0.1833

    # training / validation separation:
    data_length = len(x)
    X_train = x[:int(1 - validation_portion * data_length)]
    Y_train = y[:int(1 - validation_portion * data_length)]
    X_test = x[int(1 - validation_portion * data_length):]
    Y_test = y[int(1 - validation_portion * data_length):]
    
    # compiling net object:
    input_shape = X_train[0].shape
    model = net(input_shape)
    model.summary()

    optimizer_method = 'adam'
    model.compile(loss='binary_crossentropy', optimizer=optimizer_method, metrics=['accuracy'])

    EarlyStopping(monitor='val_loss', patience=0, verbose=1)
    checkpointer = ModelCheckpoint(model_description + '.hdf5', verbose=1, save_best_only=True)

    datagen = ImageDataGenerator(
        zoom_range=[0.6, 1.],
        featurewise_center=False,  # set input mean to 0 over the dataset
        samplewise_center=False,  # set each sample mean to 0
        featurewise_std_normalization=False,  # divide inputs by std of the dataset
        samplewise_std_normalization=False,  # divide each input by its std
        zca_whitening=False,  # apply ZCA whitening
        rotation_range=360,  # randomly rotate images in the range (degrees,output_image 0 to 180)
        width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
        height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
        horizontal_flip=True,  # randomly flip images
        vertical_flip=False)  # randomly flip images

    # compute quantities required for featurewise normalization
    # (std, mean, and principal components if ZCA whitening is applied)
    datagen.fit(X_train)

    # fit the model on the batches generated by datagen.flow()
    model.fit_generator(datagen.flow(X_train, Y_train, shuffle=True, batch_size=size_batch),
                        nb_epoch=epoches_number, verbose=1, validation_data=(X_test, Y_test),
                        callbacks=[checkpointer], class_weight=None, max_q_size=10, samples_per_epoch=len(X_train))


def emotion_detector(input_images_list):

    # fit to net:
    input_shape = (1, 50, 50)
    
    output_images_list = []
    for image in input_images_list:
        a = image.copy()

        output_image_tmp = np.reshape(a, (50, 50, 1))
        output_image = np.transpose(output_image_tmp, (2, 0, 1))
        output_images_list.append(output_image)
        output_images_list = np.array(output_images_list, dtype='float32')/255
        
        
    print(output_images_list.shape)

    # run test on image list:
    model = net(input_shape)
    current_directory_name = os.getcwd()
    model.load_weights(os.path.join(current_directory_name, 'model_weights.hdf5'))
    optimizer_method = 'adam'
    model.compile(loss='binary_crossentropy', optimizer=optimizer_method, metrics=['accuracy'])
    #probability = model.predict_proba(output_images_list, batch_size=len(output_images_list))
    classes = model.predict(output_images_list, batch_size=len(output_images_list))
    
    return classes

#train()

dataset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset")
doors_path = os.path.join(dataset_path, "doors")
not_doors_path = os.path.join(dataset_path, "not_doors")


door = os.path.join(doors_path, "2_img.svg2.png")
not_door = os.path.join(not_doors_path, "3_1_1760.png")

image = cv2.imread(not_door)
image = make_grey(image)
classes = emotion_detector([image])

print(classes)
