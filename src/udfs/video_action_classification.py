# coding=utf-8
# Copyright 2018-2020 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from src.models.catalog.frame_info import FrameInfo
from src.models.catalog.properties import ColorSpace
from src.models.storage.batch import FrameBatch
from src.models.inference.classifier_prediction import Prediction

from src.loaders.action_classify_loader import ActionClassificationLoader
from src.udfs.abstract_udfs import AbstractClassifierUDF

from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, Conv2D, Flatten


from typing import List
import numpy as np


class VideoToFrameClassifier(AbstractClassifierUDF):

    def __init__(self):
        # Build the model
        self.model = self.buildModel()

        # Train the model using shuffled data
        self.trainModel()

    def trainModel(self):
        """
        trainModel trains the built model using chunks of data of size n videos

        Inputs:
         - model = model object to be trained
         - videoMetaList = list of tuples where the first element is
                           a EVA VideoMetaInfo
                           object and the second is a string label of the
                           correct video classification
         - labelList = list of labels derived from the labelMap
         - n = integer value for how many videos to act on at a time
        """
        videoLoader = ActionClassificationLoader(1000)

        for batch, labels in videoLoader.load_video("./data/hmdb/"):
            self.labelMap = videoLoader.getLabelMap()

            # Get the frames as a numpy array
            frames = batch.frames_as_numpy_array()
            print(frames.shape)
            print(labels.shape)

            # Split x and y into training and validation sets
            xTrain = frames[0:int(0.8 * frames.shape[0])]
            yTrain = labels[0:int(0.8 * labels.shape[0])]
            xTest = frames[int(0.8 * frames.shape[0]):]
            yTest = labels[int(0.8 * labels.shape[0]):]

            # Train the model using cross-validation
            # (so we don't need to explicitly do CV outside of training)
            self.model.fit(xTrain, yTrain,
                           validation_data=(xTest, yTest), epochs=2)
            self.model.save("./data/hmdb/2d_action_classifier.h5")

    def buildModel(self):
        """
        buildModel sets up a convolutional 2D network
        using a reLu activation function

        Outputs:
         - model = model obj to be used later for training and classification
        """
        # We must incrementally train the model so
        # we'll set it up before preparing the data
        model = Sequential()

        # Add layers to the model
        model.add(Conv2D(64, kernel_size=3, activation="relu",
                         input_shape=(240, 320, 3)))
        model.add(Conv2D(32, kernel_size=3, activation="relu"))
        model.add(Flatten())
        model.add(Dense(51, activation="softmax"))

        # Compile model and use accuracy to measure performance
        model.compile(optimizer="adam",
                      loss="categorical_crossentropy", metrics=["accuracy"])

        return model

    def input_format(self) -> FrameInfo:
        return FrameInfo(240, 320, 3, ColorSpace.RGB)

    @property
    def name(self) -> str:
        return "Paula_Test_Funk"

    def labels(self) -> List[str]:
        return [
            'brush_hair', 'clap', 'draw_sword', 'fall_floor', 'handstand',
            'kick', 'pick', 'push', 'run',
            'shoot_gun', 'smoke', 'sword', 'turn', 'cartwheel', 'climb',
            'dribble', 'fencing', 'hit',
            'kick_ball', 'pour', 'pushup', 'shake_hands', 'sit', 'somersault',
            'sword_exercise', 'walk', 'catch',
            'climb_stairs', 'drink', 'flic_flac', 'hug', 'kiss', 'pullup',
            'ride_bike', 'shoot_ball', 'situp',
            'stand', 'talk', 'wave', 'chew', 'dive', 'eat', 'golf',
            'jump', 'laugh', 'punch', 'ride_horse',
            'shoot_bow', 'smile', 'swing_baseball', 'throw'
        ]

    def classify(self, batch: FrameBatch) -> List[Prediction]:
        """
        Takes as input a batch of frames and returns the
        predictions by applying the classification model.

        Arguments:
            batch (FrameBatch): Input batch of frames
            on which prediction needs to be made

        Returns:
            List[Prediction]: The predictions made by the classifier
        """

        pred = self.model.predict(batch.frames_as_numpy_array())
        return [self.labels()[np.argmax(l)] for l in pred]
