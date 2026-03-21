// Assigned to: Mai Komar
// Phase: 3 (F3.2)
//
// TODO: Message thread component for listing detail page.
//
// Props:
//   - listingId: number
//   - sellerId: number (to determine if current user is seller or buyer)
//
// Structure:
//   <div className="message-thread">
//     <h3>Messages</h3>
//     <div className="messages-list">
//       {messages.map(msg => (
//         <div className={`message ${msg.sender_id === currentUser.id ? 'sent' : 'received'}`}>
//           <span className="message-sender">{msg.sender.name}</span>
//           <p className="message-content">{msg.content}</p>
//           <span className="message-time">{formatted timestamp}</span>
//         </div>
//       ))}
//       {messages.length === 0 && <p>No messages yet. Start the conversation!</p>}
//     </div>
//     <form className="message-form" onSubmit={handleSend}>
//       <input type="text" value={newMessage} onChange={...} placeholder="Type a message..." />
//       <button type="submit">Send</button>
//     </form>
//   </div>
//
// Behavior:
//   1. On mount, call api/messages.ts getMessages(listingId)
//   2. Display messages in chronological order
//   3. Style sent messages (right-aligned) vs received (left-aligned)
//   4. On form submit, call api/messages.ts sendMessage(listingId, { content })
//   5. After sending, append new message to list (or re-fetch)
//   6. Auto-scroll to bottom on new messages
//   7. Don't show message form if user is the seller and no one has messaged yet


// Assigned to: Mai Komar (Phase 3)
// Integrated by: Harnaindeep Kaur
// src/components/MessageThread.tsx

import React, { useState, useEffect, useRef } from 'react';
import { getMessages, sendMessage } from '../api/messages'; 

// REMOVED: import './MessageThread.css'; 
// (We are using the global styles you added to index.css instead)

interface Props {
  listingId: number;
  sellerId: number;
  currentUserId: number; 
}

const MessageThread: React.FC<Props> = ({ listingId, sellerId, currentUserId }) => {
  const [messages, setMessages] = useState<any[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);

  // 1. Fetch messages on mount
  useEffect(() => {
    const fetchMsgs = async () => {
      try {
        const data = await getMessages(listingId);
        // Ensure data exists before setting
        setMessages(data?.messages || []);
      } catch (err) {
        console.error("Failed to fetch messages", err);
      } finally {
        setLoading(false);
      }
    };
    fetchMsgs();
  }, [listingId]);

  // 6. Auto-scroll to bottom when messages update
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    try {
      const sent = await sendMessage(listingId, { content: newMessage });
      setMessages([...messages, sent]); 
      setNewMessage('');
    } catch (err) {
      alert("Failed to send message.");
    }
  };

  // 7. Don't show form if user is seller and no messages exist yet
  const isSeller = currentUserId === sellerId;
  const showForm = !isSeller || messages.length > 0;

  if (loading) return <div style={{ padding: '20px', color: '#aaa' }}>Loading chat...</div>;

  return (
    <div className="message-thread">
      <h3 style={{ marginBottom: '15px' }}>Messages</h3>
      <div className="messages-list">
        {messages.map((msg) => (
          <div 
            key={msg.id} 
            className={`message ${msg.sender_id === currentUserId ? 'sent' : 'received'}`}
          >
            <span className="message-sender">{msg.sender.name}</span>
            <p className="message-content">{msg.content}</p>
            <span className="message-time">
              {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        ))}
        {/* Scroll target */}
        <div ref={scrollRef} /> 
        
        {messages.length === 0 && (
          <p className="empty-msg" style={{ textAlign: 'center', color: '#888', padding: '20px' }}>
            No messages yet. Start the conversation!
          </p>
        )}
      </div>

      {showForm && (
        <form className="message-form" onSubmit={handleSend}>
          <input 
            type="text" 
            value={newMessage} 
            onChange={(e) => setNewMessage(e.target.value)} 
            placeholder="Type a message..." 
            className="auth-input" 
            style={{ marginBottom: 0 }} // Override any bottom margin from auth-input
          />
          <button type="submit" className="btn-red-sm">Send</button>
        </form>
      )}
    </div>
  );
};

export default MessageThread;