// src/components/Chatbot/FloatingChatbot.tsx

import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Loader2, Trash2, FileText } from 'lucide-react';
import { sendChatbotMessage } from '../../services/api';
import type { ChatMessage } from '../../types/application';
import toast from 'react-hot-toast';

export const FloatingChatbot: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom whenever chat history changes
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory, isLoading]);

  // Format response to handle tables and structured data
  const formatResponse = (text: string) => {
    // Check if response contains table-like structure
    if (text.includes('|') && text.includes('---')) {
      return formatTableResponse(text);
    }
    
    // Format bold text
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Format bullet points
    text = text.replace(/^• (.+)$/gm, '<li>$1</li>');
    if (text.includes('<li>')) {
      text = text.replace(/(<li>.*<\/li>)/s, '<ul class="list-disc ml-4 space-y-1">$1</ul>');
    }
    
    // Format line breaks
    text = text.replace(/\n/g, '<br/>');
    
    return <div dangerouslySetInnerHTML={{ __html: text }} />;
  };

  // Format table responses nicely
  const formatTableResponse = (text: string) => {
    const lines = text.split('\n');
    const tableLines: string[] = [];
    const otherLines: string[] = [];
    let inTable = false;

    lines.forEach(line => {
      if (line.includes('|')) {
        tableLines.push(line);
        inTable = true;
      } else if (line.trim() === '' && inTable) {
        inTable = false;
      } else if (inTable) {
        tableLines.push(line);
      } else {
        otherLines.push(line);
      }
    });

    if (tableLines.length === 0) {
      return <div className="whitespace-pre-wrap">{text}</div>;
    }

    // Parse table
    const rows = tableLines
      .filter(line => !line.includes('---'))
      .map(line => 
        line.split('|')
          .map(cell => cell.trim())
          .filter(cell => cell.length > 0)
      );

    const header = rows[0];
    const body = rows.slice(1);

    return (
      <div className="space-y-3">
        {/* Text before table */}
        {otherLines.length > 0 && (
          <div className="text-sm text-gray-700 mb-2">
            {otherLines.join('\n')}
          </div>
        )}

        {/* Table */}
        <div className="overflow-x-auto bg-white rounded-lg border border-gray-200 shadow-sm">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-primary-50">
              <tr>
                {header.map((cell, i) => (
                  <th
                    key={i}
                    className="px-4 py-2 text-left text-xs font-semibold text-primary-700 uppercase tracking-wider"
                  >
                    {cell}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-100">
              {body.map((row, i) => (
                <tr key={i} className="hover:bg-gray-50 transition-colors">
                  {row.map((cell, j) => (
                    <td
                      key={j}
                      className="px-4 py-2 text-sm text-gray-700 whitespace-nowrap"
                    >
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    
    // Add user message immediately for better UX
    const newUserMessage: ChatMessage = {
      user: userMessage,
      assistant: '', // Will be filled after response
    };
    
    setChatHistory(prev => [...prev, newUserMessage]);
    setIsLoading(true);

    try {
      // Send message to backend
      const response = await sendChatbotMessage(userMessage, chatHistory);

      // Update the last message with assistant response
      setChatHistory(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          user: userMessage,
          assistant: response.response,
        };
        return updated;
      });
    } catch (error) {
      console.error('Chatbot error:', error);
      toast.error('Failed to get response from chatbot');
      
      // Update with error message
      setChatHistory(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          user: userMessage,
          assistant: 'Sorry, I encountered an error. Please try again.',
        };
        return updated;
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setChatHistory([]);
    toast.success('Chat history cleared');
  };

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 bg-primary-600 hover:bg-primary-700 text-white p-4 rounded-full shadow-lg transition-all hover:scale-110 z-50 flex items-center space-x-2"
          title="AI Policy Assistant"
        >
          <MessageCircle className="w-6 h-6" />
          <span className="hidden sm:inline font-medium">Ask AI</span>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-white rounded-2xl shadow-2xl flex flex-col z-50 border border-gray-200">
          {/* Header */}
          <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white p-4 rounded-t-2xl flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-white bg-opacity-20 p-2 rounded-lg">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">🏥 Policy Assistant</h3>
                <p className="text-xs text-primary-100">Ask about policy rules & risk factors</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="hover:bg-white hover:bg-opacity-20 p-1 rounded transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages Container */}
          <div
            ref={messagesContainerRef}
            className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-gray-50 to-white"
          >
            {chatHistory.length === 0 ? (
              <div className="text-center mt-8 space-y-4">
                <div className="bg-primary-50 border border-primary-200 rounded-xl p-6">
                  <div className="text-4xl mb-3">👋</div>
                  <h4 className="font-semibold text-gray-800 mb-2">Hello!</h4>
                  <p className="text-sm text-gray-600 mb-4">
                    I can help you understand policy rules, risk factors, and premium calculations.
                  </p>
                  <div className="text-left space-y-2 bg-white p-4 rounded-lg border border-primary-100">
                    <p className="text-xs font-semibold text-primary-700 uppercase">Try asking:</p>
                    <ul className="text-xs text-gray-600 space-y-1">
                      <li>• What are the BMI classifications?</li>
                      <li>• What is the smoking loading factor?</li>
                      <li>• How many users got declined?</li>
                      <li>• What are age-based premium rates?</li>
                    </ul>
                  </div>
                </div>
              </div>
            ) : (
              <>
                {chatHistory.map((message, index) => (
                  <div key={index} className="space-y-3">
                    {/* User Message */}
                    <div className="flex justify-end">
                      <div className="bg-primary-600 text-white px-4 py-2 rounded-2xl rounded-tr-sm max-w-[80%] shadow-md">
                        <p className="text-sm">{message.user}</p>
                      </div>
                    </div>

                    {/* Assistant Message */}
                    {message.assistant && (
                      <div className="flex justify-start">
                        <div className="bg-white border border-gray-200 px-4 py-3 rounded-2xl rounded-tl-sm max-w-[85%] shadow-sm">
                          <div className="text-sm text-gray-700">
                            {formatResponse(message.assistant)}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}

                {/* Loading Indicator */}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-white border border-primary-200 px-4 py-3 rounded-2xl rounded-tl-sm shadow-sm">
                      <div className="flex items-center space-x-2 text-primary-600">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span className="text-sm font-medium">Analyzing your question...</span>
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
            
            {/* Scroll anchor */}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 p-4 bg-white rounded-b-2xl">
            <div className="flex items-center space-x-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about policy rules..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none text-sm"
                disabled={isLoading}
              />
              
              {/* Send Button */}
              <button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isLoading}
                className="bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white p-2 rounded-lg transition-colors"
                title="Send message"
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>

              {/* Clear Chat Button */}
              {chatHistory.length > 0 && !isLoading && (
                <button
                  onClick={clearChat}
                  className="text-gray-400 hover:text-red-500 p-2 rounded-lg transition-colors"
                  title="Clear chat"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};
