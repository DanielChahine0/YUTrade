import client from "./client"
import { Rating, SellerRatingsOut, MyRatingOut, RatingCreate, RatingUpdate } from "../types"

export const getSellerRatings = (sellerId: number): Promise<SellerRatingsOut> =>
  client.get<SellerRatingsOut>(`/users/${sellerId}/ratings`).then(r => r.data)

export const getMyRating = (listingId: number): Promise<MyRatingOut> =>
  client.get<MyRatingOut>(`/listings/${listingId}/rating/me`).then(r => r.data)

export const createRating = (listingId: number, data: RatingCreate): Promise<Rating> =>
  client.post<Rating>(`/listings/${listingId}/rating`, data).then(r => r.data)

export const updateRating = (listingId: number, data: RatingUpdate): Promise<Rating> =>
  client.patch<Rating>(`/listings/${listingId}/rating`, data).then(r => r.data)

export const deleteRating = (listingId: number): Promise<void> =>
  client.delete(`/listings/${listingId}/rating`).then(() => undefined)
