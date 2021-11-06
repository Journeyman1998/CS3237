import { StatusBar } from 'expo-status-bar';
import React, {useState, useEffect} from 'react';
import {StyleSheet, Text, View, Button, Image } from 'react-native';
import { Camera } from 'expo-camera';
import axios from 'axios';

export default function App() {
  const [hasCameraPermission, setHasCameraPermission] = useState(null);
  const [camera, setCamera] = useState(null);
  const [image, setImage] = useState(null);
  const [type, setType] = useState(Camera.Constants.Typeback);

  const DELAY = 15000;

  const cameraStatus = async () => {
    const cameraPermission = await Camera.requestPermissionsAsync();

    setHasCameraPermission(cameraPermission.status === 'granted');
  }

  const takePicture = async () => {
    console.log("Taking picture");
    if (camera){
      const data = await camera.takePictureAsync(null);
      console.log(data.uri);
      setImage(data.uri);
      return data.uri;
    }
  }

  const sendPictureToServer = async (data) => {

    var body = new FormData();
    body.append('file', {
      uri: data, // your file path string
      name: 'latest.jpg',
      type: 'image/jpg'
    })

    fetch('http://18.142.17.12:5000/upload',
      {
        method: 'POST',
        body
      }
    );

  }

    // normally on status screen, just keeping polling for new gestures
  useEffect(() => {
    const interval = setInterval(() => {
      takePicture().then((data) => {
        sendPictureToServer(data);
      });
      
    }, DELAY);

    return () => clearInterval(interval); // This represents the unmount function, in which you need to clear your interval to prevent memory leaks.
  }, [])


  if (hasCameraPermission === false){
    return <Text>No Camera Access</Text>;
  }


  return (
    <View style={{flex:1}}>
      <View style={styles.cameraContainer}>
      <Camera ref={ref => setCamera(ref)}
      style={styles.fixedRatio}
      type={type}
      ratio={'1:1'}
      />
    </View>
    <Button
    title="Flip Camera"
    onPress={()=> {
      setType(type === Camera.Constants.Type.back ? Camera.Constants.Type.front : Camera.Constants.Type.back);
    }}></Button>
    <Button title="Take Picture"
    onPress={() => takePicture()}
    />
    {image && <Image source={{uri: image}} style={{flex:1}} />}
  
  </View>  
  );
}

const styles = StyleSheet.create({
  cameraContainer: {
    flex: 1,
    flexDirection:'row'
  },
  fixedRatio: {
    flex:1,
    aspectRatio:1
  }
})