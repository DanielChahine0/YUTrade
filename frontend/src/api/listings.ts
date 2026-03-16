// Assigned to: Mai Komar
// Phase: 2 (F2.1)
//
// TODO: Listings API functions.
//
// import client from "./client"
// import { Listing, PaginatedListings } from "../types"
//
// getListings(params: { search?, category?, status?, page?, limit? }): Promise<PaginatedListings>
//   - GET /listings with query params
//   - Return response.data
//
// getListing(id: number): Promise<Listing>
//   - GET /listings/{id}
//   - Return response.data
//
// createListing(formData: FormData): Promise<Listing>
//   - POST /listings with FormData (multipart/form-data)
//   - Must set Content-Type header to "multipart/form-data"
//   - FormData should include: title, description, price, category, and images[] files
//   - Return response.data
//
// updateListing(id: number, data: { title?, description?, price?, status? }): Promise<Listing>
//   - PATCH /listings/{id} with JSON body
//   - Return response.data


// listings.ts
import client from "./client";
import { Listing, PaginatedListings } from "../types";

export const getListings = (params?: {
  search?: string;
  category?: string;
  status?: string;
  page?: number;
  limit?: number;
}) => {
  return client.get<PaginatedListings>("/listings", { params }).then((res) => res.data);
};

export const getListing = (id: number) => {
  return client.get<Listing>(`/listings/${id}`).then((res) => res.data);
};

export const createListing = (formData: FormData) => {
  // Do NOT set headers manually — let Axios handle multipart
  return client.post<Listing>("/listings", formData).then((res) => res.data);
};

export const updateListing = (id: number, data: {
  title?: string;
  description?: string;
  price?: number;
  status?: string;
}) => {
  return client.patch<Listing>(`/listings/${id}`, data).then((res) => res.data);
};
