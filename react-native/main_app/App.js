import { StatusBar } from 'expo-status-bar';
import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, Image } from 'react-native';

const getAppStatus = async () => {
  let response = await fetch(
    'http://18.142.17.12:5000/app'
  );
  let json = await response.json();
  return json
}

const getLatestImage = async (setImage) => {
  let response = await fetch(
    'http://18.142.17.12:5000/image?' + Date.now()
  );
  let blob = await response.blob();
  
  var reader = new FileReader();
  reader.onload = () => {
    setImage(reader.result);
  }
  reader.readAsDataURL(blob);
}

export default function App() {

  const [gesture, setGesture] = useState('');  // gesture
  const [gestureId, setGestureId] = useState(0); //gesture id
  const [lastGestureId, setLastGestureId] = useState(0) // stores the last gesture id

  const [currentScreen, setCurrentScreen] = useState("status") // current state of app

  const [rawHumidity, setRawHumidity] = useState(0);
  const [humidityLevel, setHumidityLevel] = useState("Low");
  const [image, setImage] = useState('');

  const DELAY = 3000;
  const IMAGE_DELAY = 15000;

  // screen transition logic
  const getScreen = (current, newGesture) => {
    if(current === "status" && newGesture === "Swipe")
      setCurrentScreen("camera");
    else if(current === "camera" && newGesture === "Swipe")
      setCurrentScreen("status")
    else if(newGesture === "Water plant" && humidityLevel === "Low")
      setCurrentScreen("water")
  }

  const setHumidity = () => {
    if (rawHumidity < 30) {
      setHumidityLevel("Low");
    } else if (rawHumidity < 60) {
      setHumidityLevel("Med");
    } else {
      setHumidityLevel("High");
    }
  }

  // initialise the state
  useEffect(() => {

    getAppStatus().then((results) => {

      //set gesture
      setGestureId(results.id);
      setLastGestureId(results.id);
      setGesture(results.gesture);

      //set humidity
      setRawHumidity(results.humidity);
      setHumidity();

      logStates("Initialisation");
    })

    //set image
    getLatestImage(setImage);

  }, [])

  // only change back from water plant screen when humidity is normal
  useEffect(() => {
    if(humidityLevel !== "Low" && currentScreen === "water") {
      setCurrentScreen("status");
    }
  }, [humidityLevel, currentScreen])


  // normally on status screen, just keeping polling for new gestures
  useEffect(() => {
    const interval = setInterval(() => {
      getAppStatus().then((results) => {
        setGesture(results.gesture);
        setGestureId(results.id);

        setRawHumidity(results.humidity);
        setHumidity();

        logStates("Update with GET request");
      })
      
    }, DELAY);

    return () => clearInterval(interval); // This represents the unmount function, in which you need to clear your interval to prevent memory leaks.
  }, [gestureId, gesture, rawHumidity, humidityLevel])


  // normally on status screen, just keeping polling for new gestures
  useEffect(() => {
    const interval = setInterval(() => {
      getLatestImage(setImage);
      
    }, IMAGE_DELAY);

    return () => clearInterval(interval); // This represents the unmount function, in which you need to clear your interval to prevent memory leaks.
  }, [image])


  useEffect(() => {
        // if no new gesture, just skip rendering
        if(lastGestureId != gestureId) {
          logStates("Found new gestures");
          getScreen(currentScreen, gesture);
          setLastGestureId(gestureId);
        }
  }, [lastGestureId, gestureId, currentScreen, gesture])


  const logStates = (location) => {
    console.log("Logging from " + location);
    console.log("Gesture: " + gesture);
    console.log("Gesture Id: " + gestureId);
    console.log("Last gesture Id: " + lastGestureId);
    console.log("currentScreen: " + currentScreen);
    console.log("\n");
  }


  if(currentScreen === "status") {
    return <StatusScreen humidityLevel={humidityLevel} />
  }
  else if(currentScreen === "camera") {
    return <CameraScreen image={image}/>
  }
  else if(currentScreen === "water") {
    return <WaterScreen />
  }
    
}

function WaterScreen(props) {

  return (
    <View style={styles.container}>
      <Text>Watering Plant</Text>
      <StatusBar style="auto" />
    </View>
  );
}

function CameraScreen({image}) {

  return (
    <View style={styles.container}>
      <Text>Camera Screen</Text>
      <Image source={{uri: image, scale: 1}} style={{width: 500, height: 500}}/>
      <StatusBar style="auto" />
    </View>
  );
}

function StatusScreen({humidityLevel}) {

  const HumidityReadingLabel = () => {
    if (humidityLevel === "Low"){
      return <Text style={styles.humidityLow}>Low</Text>
    } else if (humidityLevel === "Med") {
      return <Text style={styles.humidityMed}>Medium</Text>
    } else if (humidityLevel === "High") {
      return <Text style={styles.humidityHigh}>High</Text>
    }
  }

  return (
    <View style={styles.container}>
      <Text>Status Screen</Text>
      <Text>Humidity: </Text>
      <HumidityReadingLabel />
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  humidityLow: {
    backgroundColor: 'red',
  },
  humidityMed: {
    backgroundColor: 'orange',
  },
  humidityHigh: {
    backgroundColor: 'green',
  }
});
