"use client";

// npm install @langchain/langgraph-sdk @langchain/core
// npm install react-markdown

import { useStream } from "@langchain/langgraph-sdk/react";
import ReactMarkdown from 'react-markdown';
import { useEffect, useState } from "react";
import "./App.css";


import CodeUI from "./component_ui/code";
import WarningUI from "./component_ui/warning"
import WeatherUI from "./component_ui/weather"
import { ScaleLoader , BounceLoader, BarLoader} from 'react-spinners'
import SimpleImageSlider from "react-simple-image-slider";

// import CodeUI from "./component/code_ui"; 
// import { BarLoader } from 'react-css-loaders'; //not work give error




{/* <ReactMarkdown>{report}</ReactMarkdown> */}


export default function App() {

    const [clicked, setClicked] = useState(false);

  const [partialResponse ,setPartialResponse] =useState("")
    const [finalMessages, setFinalMessages] = useState([]);
    const [user,setUser] = useState("")
//   useEffect(() => {
// console.log(partialResponse)
// }, [partialResponse]);

//  console.log('refreshed')
  const thread = useStream({
    // apiUrl: "http://127.0.0.1:8989", 
    apiUrl: "http://127.0.0.1:5555",
    assistantId: "agent",
    messagesKey: "messages",
    onFinish:(finalevent)=>{
      setPartialResponse("")
      // setFinalMessages(thread.messages); 
      //state stream after node return state
      console.log(finalevent.values.messages)
      setFinalMessages(finalevent.values.messages); 
      ; // clear partial
      setUser("")
      },

      onError:()=>{setPartialResponse("")},

    onStop:()=>{ setPartialResponse("")}, 

    onCustomEvent: (event, options) => {
      console.log(event)
       setPartialResponse(event)}    //for custom data stream by get_stream_writer
    
    // onCustomEvent: for custom event handler
    
  });

// useEffect(()=>{thread.events.forEach(element => {
  
// });((e)=>{console.log(e)})})

 const sampleImages = [
    "https://picsum.photos/400/250?random=1",
    "https://picsum.photos/400/250?random=2",
    "https://picsum.photos/400/250?random=3",
  ];

  return (<div className="layout">
         {/* <BarLoader /> */}
          <div className="user-query">

  <div style={{ textAlign: "center" ,marginBottom:'10px',color:'white' }}>
    User Query
  </div>








{/* when query in history click scrollToViewElement() chat-container element*/}
  <div className="messages">
    {finalMessages
       ?.slice()
       ?.reverse()
      ?.filter((msg) => msg.type === "human" && msg.content.trim() !=='') // only user messages
      ?.map((msg) => (
        <div key={msg.id}  onClick={()=>{console.log(msg.content); setClicked(!clicked);const  e =document.getElementById(msg.id); e.scrollIntoView({behavior:'smooth',block:'center'})  }} className="user-bubble">
          {msg.content}
        </div>
      ))}
  </div>
</div>











    <div className="chat-container">

 <div className="messages">

        {/* {thread.messages.map((msg) => ( */}
        {/* <CodeUI code='python and javaScript code here' /> */}

        {
        // finalMessages?.map((msg) => ( 
        //   <div
        //   key={msg.id}
        //   id={msg.id}
        //   className={`message ${msg.type==="human"? "user": "bot"}`}
        //   >
        //     {/* <ReactMarkdown>{msg.content}</ReactMarkdown>  */}
        //   {msg.name==='warning' && msg.type==="ai" && (<div > <ReactMarkdown color={'red'}>{msg.content}</ReactMarkdown> </div>)}
        //   {msg.type==='human' && ( <ReactMarkdown>{msg.content}</ReactMarkdown> )}
        //   {msg.type==='ai' && (<ReactMarkdown>{msg.content}</ReactMarkdown>)}
        //   {msg.name==='weather' && (<div >weather </div>)}
        //   {msg.name==='images' && (<div >image slider</div>)}
        //   {msg.name==='report' && (<div >report ui</div>)}
        //   {msg.name==='code' && (<div >code ui</div>)}

        //   </div>
        //  ))
         }



         {finalMessages?.map((msg) => (
  <div
    key={msg.id}
    id={msg.id}
    className={`message ${msg.type === "human" ? "user" : "bot"}`}
  >
    {msg.name === "warning" && msg.type === "ai" ? (
      <div>
        <WarningUI  message={msg.content}/>        {/* <ReactMarkdown>{msg.content}</ReactMarkdown> */}
      </div>
    ) : msg.name === "weather_tool" ? (
 <WeatherUI city="Mumbai" temperature={32} condition="Sunny" />
      // <WeatherUI city={msg.additional_kwargs['city']}  temperature={msg.additional_kwargs['temperature']} condition={msg.additional_kwargs['condition']} />
    ) : msg.name === "images" ? ( <div style={{display:"flex" , flexDirection:'row'}}>
   {/* <SimpleImageSlider  /> */}
   <div >
      <SimpleImageSlider
        width={500}
        height={304}
        images={sampleImages}
        showBullets={true}
        showNavs={true}
        autoPlay={true}
        autoPlayDelay={2}
        slideDuration={2}

      />
    </div> 
          </div>
    ) : msg.name === "report" ? (
      <div>report ui</div>
    ) : msg.name === "code" ? (  
       <CodeUI code={msg.content} language="javascript" />
    ) : msg.type === "human" ? (
      <ReactMarkdown>{msg.content}</ReactMarkdown>
    ) : msg.type === "ai" ? (
      <ReactMarkdown>{msg.content}</ReactMarkdown>
    ) : null}
  </div>
))}



        {/* //user message temp. until receive final state  */}
        {user && ( <div className="message user">
            <ReactMarkdown>{user}</ReactMarkdown>
          </div>)}
         






        {/* Live-streaming partial output */}
        {partialResponse && (
          <div className="message bot">
             
            <ReactMarkdown>{partialResponse}</ReactMarkdown>
            <BarLoader width={200} />
          </div>
        )}
      </div>




      {/* Input bar */}
      <form
        className="input-bar"
        onSubmit={(e) => {
          e.preventDefault();
          const form = e.target;
          const message = new FormData(form).get("message");
          form.reset();
          setUser(message)



  thread.submit({ //values(stateKey):value
          messages:[message]

          },
          {streamMode:["custom"], streamSubgraphs:true });

  }}
      >
       <label  for='file' style={{margin:"10px"}}>➕
        </label>
         <input type="file" id="file" className="file_upload" />

        {/* Input */}
        <input
          type="text"
          name="message"
          placeholder="Ask a question..."
          autoComplete="off"
        />

        {/* Send/Stop Button */}
        {thread.isLoading ? (
          <button type="button" onClick={() => thread.stop()}>
            Stop
          </button>
        ) : (
          <button type="submit">Send</button>
        )}
      </form>
    </div>
     </div>
  );
}