import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Send, Upload, FileText, Trash2 } from 'lucide-react';
import './index.css';

interface Message {
  id: number;
  type: 'user' | 'assistant';
  content: string;
  source?: 'knowledge_base' | 'qianwen_api';
  timestamp: Date;
}

interface Document {
  id: number;
  filename: string;
  created_at: string;
  content_length: number;
}

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchDocuments();
    // 添加欢迎消息
    setMessages([{
      id: 1,
      type: 'assistant',
      content: '您好！我是您的AI助手。您可以直接与我对话，或者上传PDF文件来构建知识库。我会优先从知识库中寻找答案。',
      timestamp: new Date()
    }]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchDocuments = async () => {
    try {
      const response = await axios.get('/api/documents');
      setDocuments(response.data.documents);
    } catch (error) {
      console.error('获取文档列表失败:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || loading) return;

    const userMessage: Message = {
      id: messages.length + 1,
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await axios.post('/api/chat', {
        message: inputMessage
      });

      const assistantMessage: Message = {
        id: messages.length + 2,
        type: 'assistant',
        content: response.data.response,
        source: response.data.source,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: messages.length + 2,
        type: 'assistant',
        content: '抱歉，发生了错误。请检查后端服务是否正常运行，或确认API密钥配置是否正确。',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleFileUpload = async (file: File) => {
    if (!file.type.includes('pdf')) {
      alert('只支持PDF文件上传');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      alert(`文件上传成功：${response.data.filename}`);
      fetchDocuments();
    } catch (error: any) {
      alert(`上传失败：${error.response?.data?.error || '未知错误'}`);
    } finally {
      setUploading(false);
    }
  };

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const deleteDocument = async (docId: number) => {
    if (!window.confirm('确定要删除这个文档吗？')) return;

    try {
      await axios.delete(`/api/documents/${docId}`);
      fetchDocuments();
    } catch (error) {
      alert('删除失败');
    }
  };

  return (
    <div className="container">
      <div className="header">
        <h1>AI Agent 对话系统</h1>
        <p>基于阿里千问API的智能对话助手</p>
      </div>

      <div className="main-content">
        <div className="chat-section">
          <div className="chat-messages">
            {messages.map((message) => (
              <div key={message.id} className={`message ${message.type}`}>
                <div className="message-content">
                  {message.content}
                  {message.source && (
                    <div className="message-source">
                      来源: {message.source === 'knowledge_base' ? '知识库' : '千问API'}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="loading">
                <div className="spinner"></div>
                <span>AI正在思考中...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input">
            <div className="input-container">
              <textarea
                className="message-input"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="输入您的问题..."
                rows={1}
              />
              <button
                className="send-button"
                onClick={sendMessage}
                disabled={loading || !inputMessage.trim()}
              >
                <Send size={20} />
              </button>
            </div>
          </div>
        </div>

        <div className="sidebar">
          <div className="upload-section">
            <h3>📚 知识库管理</h3>
            <div
              className="upload-area"
              onClick={() => fileInputRef.current?.click()}
              onDrop={handleFileDrop}
              onDragOver={(e) => e.preventDefault()}
            >
              <Upload size={32} color="#007bff" />
              <p>点击或拖拽上传PDF文件</p>
              <p style={{ fontSize: '0.8em', color: '#666' }}>
                支持PDF格式，最大16MB
              </p>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              className="file-input"
            />
            {uploading && (
              <div className="loading">
                <div className="spinner"></div>
                <span>上传中...</span>
              </div>
            )}
          </div>

          <div className="documents-list">
            <h4>已上传文档 ({documents.length})</h4>
            {documents.map((doc) => (
              <div key={doc.id} className="document-item">
                <div className="document-info">
                  <div className="document-name">
                    <FileText size={16} style={{ marginRight: '5px' }} />
                    {doc.filename}
                  </div>
                  <div className="document-meta">
                    {new Date(doc.created_at).toLocaleDateString()} •
                    {Math.round(doc.content_length / 1000)}KB
                  </div>
                </div>
                <button
                  className="delete-button"
                  onClick={() => deleteDocument(doc.id)}
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
            {documents.length === 0 && (
              <p style={{ color: '#666', textAlign: 'center', padding: '20px' }}>
                暂无文档，请上传PDF文件
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
