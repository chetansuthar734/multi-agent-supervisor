// // show weather ui componet messages.name==weather

// import React from "react";
// import { Sun, CloudRain, Cloud, CloudSun, Snowflake } from "lucide-react";

// const WeatherUI = ({ city, temperature, condition }) => {
//   // Pick icon based on condition
//   const getIcon = () => {
//     switch (condition.toLowerCase()) {
//       case "sunny":
//         return <Sun className="text-yellow-500 w-10 h-10" />;
//       case "cloudy":
//         return <Cloud className="text-gray-500 w-10 h-10" />;
//       case "rainy":
//         return <CloudRain className="text-blue-500 w-10 h-10" />;
//       case "snowy":
//         return <Snowflake className="text-blue-300 w-10 h-10" />;
//       default:
//         return <CloudSun className="text-orange-400 w-10 h-10" />;
//     }
//   };

//   return (
//     <div className="flex items-center justify-between w-64 p-4 my-3 bg-blue-100 rounded-2xl shadow-md">
//       <div>
//         <h2 className="text-lg font-bold text-gray-800">{city}</h2>
//         <p className="text-2xl font-semibold text-gray-900">{temperature}°C</p>
//         <p className="text-gray-600 capitalize">{condition}</p>
//       </div>
//       <div>{getIcon()}</div>
//     </div>
//   );
// };

// export default WeatherUI;




import React from "react";
import { Sun, CloudRain, Cloud, CloudSun, Snowflake } from "lucide-react";

const WeatherUI = ({ city, temperature, condition }) => {
  // Pick icon based on condition
  const getIcon = () => {
    switch (condition.toLowerCase()) {
      case "sunny":
        return <Sun className="text-yellow-300 w-12 h-12 drop-shadow-lg" />;
      case "cloudy":
        return <Cloud className="text-gray-200 w-12 h-12 drop-shadow-lg" />;
      case "rainy":
        return <CloudRain className="text-blue-300 w-12 h-12 drop-shadow-lg" />;
      case "snowy":
        return <Snowflake className="text-white w-12 h-12 drop-shadow-lg" />;
      default:
        return <CloudSun className="text-orange-300 w-12 h-12 drop-shadow-lg" />;
    }
  };

  return (
    <div className="w-72 p-5 my-4 rounded-2xl shadow-xl text-white 
                    bg-gradient-to-r from-blue-500 via-blue-400 to-indigo-500
                    flex justify-between items-center">
      <div>
        <h2 className="text-xl font-bold">{city}</h2>
        <p className="text-4xl font-extrabold">{temperature}°C</p>
        <p className="capitalize text-gray-100">{condition}</p>
      </div>
      <div>{getIcon()}</div>
    </div>
  );
};

export default WeatherUI;
