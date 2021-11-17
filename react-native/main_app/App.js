import { StatusBar } from 'expo-status-bar';
import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, Image, SafeAreaView, Button, TextInput } from 'react-native';

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

  const [lowThreshold, setLowThreshold] = useState(30);
  const [highThreshold, setHighThreshold] = useState(60);

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
    if (rawHumidity < lowThreshold) {
      setHumidityLevel("Low");
    } else if (rawHumidity < highThreshold) {
      setHumidityLevel("Med");
    } else {
      setHumidityLevel("High");
    }
  }

  const setThresholds = (low, high) => {
    if(low !==  "") {
      setLowThreshold(parseInt(low, 10))
    }

    if(high !== "") {
      setHighThreshold(parseInt(high, 10));
    }
    
    sendHumidityToServer();
  }


  const sendHumidityToServer = async () => {

    var body = new FormData();
    body.append('action', "update_threshold");
    body.append('payload', {'low': lowThreshold, 'high': highThreshold});

    fetch('http://18.142.17.12:5000/action',
      {
        method: 'POST',
        body
      }
    );

    return "Success";
  }

  // only change back from water plant screen when humidity is normal
  useEffect(() => {
    if(humidityLevel === "High" && currentScreen === "water") {
      setCurrentScreen("status");
    }
  }, [humidityLevel, currentScreen])


  useEffect(() => {
    setHumidity();
  }, [lowThreshold, highThreshold])


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

      //set thresholds
      setLowThreshold(results.config["low_threshold"])
      setHighThreshold(results.config["high_threshold"])

      setCurrentScreen("status");
      logStates("Initialisation");
    })

    //set image
    getLatestImage(setImage);

  }, [])


  const logStates = (location) => {
    console.log("Logging from " + location);
    console.log("Gesture: " + gesture);
    console.log("Gesture Id: " + gestureId);
    console.log("Last gesture Id: " + lastGestureId);
    console.log("currentScreen: " + currentScreen);
    console.log("\n");
  }


  if(currentScreen === "status") {
    return <StatusScreen 
    humidityLevel={humidityLevel} 
    lowHumidityThreshold={lowThreshold} 
    highHumidityThreshold={highThreshold} 
    setHumidityThresholds={setThresholds}/>
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
      <Text style={{color:'#000000', fontSize:40}}>Watering Plant...</Text>
      <StatusBar style="auto" />
    </View>
  );
}

function CameraScreen({image, startGestureRecording}) {

  return (
    <View style={styles.container}>
      <Text style={{color:'#000000', fontSize:40}}>
        Mr.Plant says HI :) </Text>
      <Image source={{uri: image, scale: 1}} style={{width: 500, height: 500}}/>
      <StatusBar style="auto" />
    </View>
  );
}

function StatusScreen({humidityLevel, lowHumidityThreshold, highHumidityThreshold, setHumidityThresholds}) {
  
  const [lowText, setLow] = useState(lowHumidityThreshold.toString());
  const [highText, setHigh] = useState(highHumidityThreshold.toString());

  const HumidityReadingLabel = () => {
    if (humidityLevel === "Low"){
      return <Text style={styles.humidityLow}>               LOW</Text>
    } else if (humidityLevel === "Med") {
      return <Text style={styles.humidityMed}>           MEDIUM</Text>
    } else if (humidityLevel === "High") {
      return <Text style={styles.humidityHigh}>              HIGH</Text>
    }
  }


  return (
    <View style={styles.container}>
      <SafeAreaView>
      <Text style={{color:'#000000', fontSize:40}}>
        Status Screen</Text>
      <Text style={{color:'#000000', fontSize:40}}>
        Humidity:</Text>
      <HumidityReadingLabel />
      <Text style={{color:'#000000', fontSize:40}}> 
        Warning:</Text>
      <TextInput
        style={styles.input}
        onChangeText={setLow}
        value={lowText}
        placeholder="Set threshold for humidity warning"
        keyboardType="numeric"
      />
      <Text style={{color:'#000000', fontSize:40}}>
        Accepted:</Text>
      <TextInput
        style={styles.input}
        onChangeText={setHigh}
        value={highText}
        placeholder="Set threshold for accepted humidity"
        keyboardType="numeric"
      />
      <Button onPress={() => setHumidityThresholds(lowText, highText)} title="Set Threshold" />
      <StatusBar style="auto" />
    </SafeAreaView>
    </View>
  );
}


const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#C6E2E9',
    alignItems: 'center',
    justifyContent: 'center',
  },
  humidityLow: {
    backgroundColor: 'red',
    fontSize:40,
  },
  humidityMed: {
    backgroundColor: 'orange',
    fontSize:40,
  },
  humidityHigh: {
    backgroundColor: 'green',
    fontSize:40,
  },
  input: {
    height: 70,
    margin: 20,
    borderWidth: 3,
    padding: 20,
    fontSize: 25,
  },
});
