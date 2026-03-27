// Assigned to: Harnaindeep Kaur
// Phase: 1 (F1.3)
//
// TODO: Define all TypeScript interfaces used across the frontend.
//
// User:
//   id: number
//   email: string
//   name: string
//   is_verified: boolean
//   created_at: string  (ISO datetime string)
//
// TokenResponse:
//   access_token: string
//   token_type: string
//   user: User
//
// Listing:
//   id: number
//   seller_id: number
//   seller: { id: number; name: string; email: string }
//   title: string
//   description: string | null
//   price: number
//   category: string | null
//   status: "active" | "sold" | "removed"
//   images: Image[]
//   created_at: string
//   updated_at: string
//
// Image:
//   id: number
//   file_path: string
//   position: number
//
// PaginatedListings:
//   listings: Listing[]
//   total: number
//   page: number
//   limit: number
//
// Message:
//   id: number
//   listing_id: number
//   sender_id: number
//   receiver_id: number
//   sender: { id: number; name: string }
//   content: string
//   created_at: string
//
// RegisterRequest:
//   email: string
//   password: string
//   name: string
//
// LoginRequest:
//   email: string
//   password: string
//
// VerifyRequest:
//   email: string
//   code: string
//
// ListingCreateForm:
//   title: string
//   description: string
//   price: number
//   category: string
//   images: File[]
//
// MessageCreateRequest:
//   content: string

export interface User {
    id: number
    email: string
    name: string
    is_verified: boolean
    created_at: string
}
export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Image {
  id: number;
  file_path: string;
  position: number;
}

export interface Listing {
  id: number;
  seller_id: number;
  seller: { id: number; name: string; email: string; created_at: string };
  title: string;
  description: string | null;
  price: number;
  category: string | null;
  status: "active" | "sold" | "removed";
  images: Image[];
  created_at: string;
  updated_at: string;
}

export interface PaginatedListings {
  listings: Listing[];
  total: number;
  page: number;
  limit: number;
}

export interface Message {
  id: number;
  listing_id: number;
  sender_id: number;
  receiver_id: number;
  sender: { id: number; name: string };
  content: string;
  created_at: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface ListingCreateForm {
  title: string;
  description: string;
  price: number;
  category: string;
  images: File[];
}

export interface MessageCreateRequest {
  content: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  email: string;
  code: string;
  new_password: string;
}

export interface ListingUpdate {
  title?: string;
  description?: string;
  price?: number;
  category?: string;
  status?: "active" | "sold" | "removed";
}

export interface RaterOut {
  id: number;
  name: string;
}

export interface Rating {
  id: number;
  listing_id: number;
  seller_id: number;
  rater_id: number;
  rater: RaterOut;
  score: number;
  comment: string | null;
  created_at: string;
}

export interface SellerOut {
  id: number;
  name: string;
  created_at: string;
}

export interface SellerRatingsOut {
  ratings: Rating[];
  average_score: number | null;
  total_count: number;
  seller?: SellerOut;
}

export interface MyRatingOut {
  rating: Rating | null;
  can_rate: boolean;
}

export interface RatingCreate {
  score: number;
  comment?: string;
}

export interface RatingUpdate {
  score?: number;
  comment?: string;
}

export interface UpdateProfileRequest {
  name: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface DeleteAccountRequest {
  password: string;
}
