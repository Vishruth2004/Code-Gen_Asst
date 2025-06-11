import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'; // choose your theme
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [file, setFile] = useState(null);

  const discardChat = () => {
    window.location.reload();
  };

  // Initialize chat with a greeting message
  useEffect(() => {
    setMessages([{ text: 'Hello, how can I help you today?', user: 'bot' }]);
  }, []);

  const handleInputChange = (e) => {
    setInput(e.target.value);
    // Auto-resize the textarea
    e.target.style.height = 'auto';
    e.target.style.height = `${e.target.scrollHeight}px`;
  };

  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSend = () => {
    if (input.trim() || file) {
      const newMessage = { text: input, user: 'me', file };
      setMessages([...messages, newMessage]);

      if (file) {
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64Image = reader.result.split(',')[1];
          sendMessage(input, base64Image);
        };
        reader.readAsDataURL(file);
      } else {
        sendMessage(input, null);
      }

      setInput('');
      setFile(null);
    }
  };

  const sendMessage = (message, image) => {
    fetch('http://localhost:5000/message', {
      method: 'POST',
      body: JSON.stringify({ message, image }),
      headers: {
        'Content-Type': 'application/json'
      }
    })
      .then(response => response.json())
      .then(data => {
        const lines = data.reply.split('\n'); // Split the reply by new lines
        setMessages(prevMessages => [...prevMessages, { text: lines, user: 'bot' }]);
      });
  };

  return (
    <div className="App dark-theme">
      <div className="chat-header">
        <h1>Claude Chatbot</h1>
        <button onClick={discardChat} className="discard-button">Discard Chat</button>
      </div>
      <div className="chat-container">
        <div className="chat-window">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.user}`}>
            {message.file && (
              <img 
                src={URL.createObjectURL(message.file)} 
                alt="Sent file" 
                className="file-preview" 
              />
            )}
            <ReactMarkdown
              components={{
                code({node, inline, className, children, ...props}) {
                  const match = /language-(\w+)/.exec(className || '');
                  return !inline ? (
                    <div className="markdown-code-block">
                      <SyntaxHighlighter
                        style={oneDark}
                        language={match ? match[1] : null}
                        PreTag="div"
                        {...props}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    </div>
                  ) : (
                    <code className="inline-code" {...props}>
                      {children}
                    </code>
                  );
                }
              }}
            >
              {typeof message.text === 'string' ? message.text : message.text.join('\n')}
            </ReactMarkdown>
          </div>
        ))}
        </div>
        {file && (
          <div className="file-preview-area">
            <img 
              src={URL.createObjectURL(file)} 
              alt="File preview" 
              className="file-preview" 
            />
            <button onClick={() => setFile(null)} className="remove-file">
              Remove
            </button>
          </div>
        )}
        <div className="chat-input">
          <div className="input-wrapper">
            <textarea
              value={input}
              onChange={handleInputChange}
              placeholder="Type Your Message Here"
              className="text-prompt"
            />
            <input
              type="file"
              onChange={handleFileChange}
              accept="image/*"
              id="file-upload"
              style={{display: 'none'}}
            />
            <label htmlFor="file-upload" className="file-upload-label">
              {file ? file.name : 'Upload'}
            </label>
          </div>
          <button onClick={handleSend} className="send-button">Send</button>
        </div>
      </div>
    </div>
  );
}

export default App;
