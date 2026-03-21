// Assigned to: Harnaindeep Kaur
// Phase: 3 (F3.4)
//
// TODO: Page showing all message conversations (protected).
//
// Layout:
//   - Page title: "Messages"
//   - List of conversation threads, grouped by listing
//   - Each thread shows:
//       - Listing title and thumbnail
//       - Other person's name
//       - Last message preview (truncated)
//       - Timestamp of last message
//   - Clicking a thread navigates to /listings/{id} (with message section visible)
//   - Empty state: "No messages yet"
//
// Behavior:
//   1. On mount, fetch all listings where the user has sent or received messages
//      (This may require a dedicated endpoint or fetching from multiple listing threads)
//   2. Display threads sorted by most recent message first
//   3. Show loading spinner while fetching
//   4. Handle errors gracefully
//
// Note: The exact API approach for getting "all threads" may need coordination
// with Raj's backend implementation. Options:
//   a) A new GET /messages endpoint that returns all threads for the current user
//   b) Client-side aggregation from multiple listing message endpoints
//   Discuss with Raj to decide the best approach.



// Assigned to: Harnaindeep Kaur
// Phase: 3 (F3.4) - The Inbox Page

import React, { useState, useEffect } from "react";
import { formatDate } from "../utils/validators";

const MessagesPage: React.FC = () => {
  const [threads, setThreads] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchThreads = async () => {
      try {
        // Mocking an empty state for now
        setLoading(false);
      } catch (err) {
        console.error("Failed to load inbox", err);
        setLoading(false);
      }
    };
    fetchThreads();
  }, []);

  if (loading) {
    return (
      <div className="app-content" style={{ textAlign: "center", paddingTop: 48 }}>
        <div className="loading-spinner">Loading your messages...</div>
      </div>
    );
  }

  return (
    <div className="app-content">
      {/* SIMPLE HEADER */}
      <div style={{ 
        marginBottom: '32px',
        paddingBottom: '16px',
        borderBottom: '1px solid #eee' 
      }}>
        <h1 className="all-listings-title" style={{ margin: 0 }}>Your Messages</h1>
        <p style={{ color: '#666', fontSize: '14px', marginTop: '4px' }}>
          Manage your conversations with buyers and sellers here.
        </p>
      </div>

      {threads.length === 0 ? (
        <div className="listings-table-wrap" style={{ 
          padding: '80px 20px', 
          textAlign: 'center', 
          background: 'var(--yu-white)',
          border: '1px solid var(--border-color)',
          borderRadius: 'var(--radius-lg)'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>💬</div>
          <h3 style={{ marginBottom: '8px' }}>No messages yet</h3>
          <p style={{ color: '#888', maxWidth: '450px', margin: '0 auto' }}>
            When you contact a seller or someone interests in your listing, 
            the chat will appear here.
          </p>
        </div>
      ) : (
        <div className="threads-container">
          {threads.map((thread) => (
            <div 
              key={thread.id} 
              className="thread-card" 
              style={{ 
                padding: '16px',
                borderBottom: '1px solid var(--gray-200)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}
            >
              <div>
                <div style={{ fontWeight: 700 }}>{thread.listing_title}</div>
                <div style={{ fontSize: '14px', color: '#555' }}>{thread.last_message}</div>
              </div>
              <div style={{ fontSize: '12px', color: '#999' }}>
                {formatDate(thread.updated_at)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MessagesPage;