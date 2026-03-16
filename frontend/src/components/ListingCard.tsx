// Assigned to: Harnaindeep Kaur
// Phase: 2 (F2.2)
//
// TODO: Card component for displaying a listing in the browse grid.
//
// Props:
//   - listing: Listing (from types/index.ts)
//
// Structure:
//   <div className="listing-card" onClick={() => navigate(`/listings/${listing.id}`)}>
//     <div className="listing-card-image">
//       {listing.images.length > 0
//         ? <img src={`${API_URL}/${listing.images[0].file_path}`} alt={listing.title} />
//         : <div className="no-image-placeholder">No Image</div>
//       }
//     </div>
//     <div className="listing-card-body">
//       <h3 className="listing-card-title">{listing.title}</h3>
//       <p className="listing-card-price">${listing.price.toFixed(2)}</p>
//       {listing.category && <span className="listing-card-category">{listing.category}</span>}
//       <p className="listing-card-date">{formatted date}</p>
//     </div>
//   </div>
//
// Styling:
//   - Card with border/shadow, rounded corners
//   - Image takes top portion, fixed aspect ratio
//   - Price in bold, possibly YU red color
//   - Category as a small badge/tag
//   - Hover effect (slight shadow increase or scale)



import React from "react"
import { useNavigate } from "react-router-dom"
import { Listing } from "../types"

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000"

interface ListingCardProps {
  listing: Listing
}

const ListingCard: React.FC<ListingCardProps> = ({ listing }) => {
  const navigate = useNavigate()

  const formattedDate = new Date(listing.created_at).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  })

  return (
    <div className="listing-card" onClick={() => navigate(`/listings/${listing.id}`)}>
      <div className="listing-card-img">
        {listing.images?.length > 0 ? (
          <img
            src={`${API_URL}/${listing.images[0].file_path}`}
            alt={listing.title}
            onError={(e) => {
              (e.target as HTMLImageElement).src =
                "https://via.placeholder.com/300?text=No+Image"
            }}
          />
        ) : (
          <div className="no-image-placeholder">No Image</div>
        )}
      </div>

      <div className="listing-card-body">
        <h3 className="listing-card-title">{listing.title}</h3>
        <p className="listing-card-price">${listing.price.toFixed(2)}</p>
        {listing.category && <p className="listing-card-category">{listing.category}</p>}
        <p className="listing-card-date">{formattedDate}</p>
      </div>
    </div>
  )
}

export default ListingCard