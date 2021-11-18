import React, {useEffect, useState} from 'react';

// import components to use
import {
  SafeAreaView,
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
} from 'react-native';

const DELAY = 3000;

//Request Optical sensor values from server
// const getLatestLux = async(readLux) => {
//   let response = await fetch(
//     'http://18.147.12:5000/intensity' + Date.now() 
//   ); 
//   let blob = await response.blob();
  
//   var reader = new FileReader();
//   reader.onload = () => {
//     readLux(reader.result);
//   }
//   reader.readAsDataURL(blob);
// }

//Switch ON/OFF logic
// const toggleSwitch = (currentLux) => {
//   currentLux = getLatestLux(readLux);
//   if(currentLux <= 10) {
//     Torch.switchState(true);
//   }
//   else {
//     Torch.switchState(false)    
//   }
// }


// import Torch Component
import Torch from 'react-native-torch';

const App = () => {
  //Default Keep Awake off
  const [isTorchOn, setIsTorchOn] = useState(false);
  const [brightness, setBrightness] = useState(1000);

  // getLatestLux(readLux);
  // // use ON/OFF logic
  // toggleSwitch(currentLux);
  
  const handlePress = () => {
    Torch.switchState(!isTorchOn);
    setIsTorchOn(!isTorchOn);
  };
  
  
  const getAppStatus = async () => {
  let response = await fetch(
    'http://18.142.17.12:5000/app'
  );
  let json = await response.json();
  return json
}

  useEffect(() => {
    const interval = setInterval(() => {
      getAppStatus().then((results) => { setBrightness(results.intensity) });
      
    }, DELAY);

    return () => clearInterval(interval); // This represents the unmount function, in which you need to clear your interval to prevent memory leaks.
  }, [])
  
  useEffect(() => {
    let toTurnOn = brightness < 10;
    Torch.switchState(toTurnOn);
		setIsTorchOn(toTurnOn);
  }, [brightness])

  return (
    <SafeAreaView style={styles.container}>
      <View>
        <Text style={styles.titleText}>
          Turn on/off Flashlight
        </Text>
        <TouchableOpacity
          activeOpacity={0.7}
          style={styles.buttonStyle}
          onPress={handlePress}>
          <Text style={styles.buttonTextStyle}>
            {isTorchOn ? 'Turn off the Torch' : 'Turn on the Torch'}
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

export default App;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'white',
    padding: 10,
    justifyContent: 'center',
  },
  titleText: {
    fontSize: 22,
    textAlign: 'center',
    fontWeight: 'bold',
  },
  buttonStyle: {
    justifyContent: 'center',
    marginTop: 15,
    padding: 10,
    backgroundColor: '#8ad24e',
    marginRight: 2,
    marginLeft: 2,
  },
  buttonTextStyle: {
    color: '#fff',
    textAlign: 'center',
  },
});