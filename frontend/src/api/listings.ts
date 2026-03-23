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

import client from "./client";
import { Listing, PaginatedListings } from "../types";

export type GetListingsParams = {
  search?: string;
  category?: string;
  status?: string;
  min_price?: number;
  max_price?: number;
  sort?: "newest" | "price_low_to_high" | "price_high_to_low";
  date_listed?: "last_24_hours" | "last_7_days" | "last_30_days";
  page?: number;
  limit?: number;
};

export const getListings = (params?: GetListingsParams) => {
  return client.get<PaginatedListings>("/listings", { params }).then((res) => res.data);
};

export const getListing = (id: number) => {
  return client.get<Listing>(`/listings/${id}`).then((res) => res.data);
};

export const createListing = (formData: FormData) => {
  return client.post<Listing>("/listings", formData, {
    headers: {
      "Content-Type": undefined,
    },
  }).then((res) => res.data);
};

export const updateListing = (
  id: number,
  data: {
    title?: string;
    description?: string;
    price?: number;
    category?: string;
    status?: string;
    newImages?: File[];
    deleteImageIds?: number[];
  }
) => {
  const formData = new FormData();
  if (data.title !== undefined) formData.append("title", data.title);
  if (data.description !== undefined) formData.append("description", data.description);
  if (data.price !== undefined) formData.append("price", String(data.price));
  if (data.category !== undefined) formData.append("category", data.category);
  if (data.status !== undefined) formData.append("status", data.status);
  if (data.newImages) {
    data.newImages.forEach((file) => formData.append("new_images", file));
  }
  if (data.deleteImageIds) {
    data.deleteImageIds.forEach((imgId) => formData.append("delete_image_ids", String(imgId)));
  }
  return client.patch<Listing>(`/listings/${id}`, formData, {
    headers: { "Content-Type": undefined },
  }).then((res) => res.data);
};
