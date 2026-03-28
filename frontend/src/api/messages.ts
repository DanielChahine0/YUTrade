// Assigned to: Mai Komar
// Phase: 3 (F3.1)
//
// TODO: Messages API functions.
//
// import client from "./client"
// import { Message, MessageCreateRequest } from "../types"
//
// sendMessage(listingId: number, data: MessageCreateRequest): Promise<Message>
//   - POST /listings/{listingId}/messages with { content }
//   - Return response.data
//
// getMessages(listingId: number): Promise<{ messages: Message[] }>
//   - GET /listings/{listingId}/messages
//   - Return response.data

import client from "./client";
import { Message, MessageCreateRequest } from "../types";

export const sendMessage = (listingId: number, data: MessageCreateRequest) => {
  return client.post<Message>(`/listings/${listingId}/messages`, data).then((res) => res.data);
};

export const getMessages = (listingId: number) => {
  return client.get<{ messages: Message[] }>(`/listings/${listingId}/messages`).then((res) => res.data);
};

export const getAllThreads = () => {
  return client.get<{ threads: any[] }>(`/messages/threads`).then((res) => res.data)
}

export const markMessagesRead = (listingId: number) => {
  return client.put<{ marked_read: number }>(`/listings/${listingId}/messages/read`).then((res) => res.data)
}