import React, { useState } from "react"

interface StarRatingProps {
  rating: number
  max?: number
  onSelect?: (score: number) => void
  size?: number
}

export default function StarRating({ rating, max = 5, onSelect, size }: StarRatingProps) {
  const [hovered, setHovered] = useState<number | null>(null)
  const interactive = !!onSelect
  const displayRating = hovered !== null ? hovered : rating

  return (
    <div
      className={`star-row${interactive ? " star-picker" : ""}`}
      onMouseLeave={() => interactive && setHovered(null)}
    >
      {Array.from({ length: max }).map((_, i) => {
        const score = i + 1
        const filled = i < Math.floor(displayRating)
        const half = !filled && i < displayRating
        return (
          <span
            key={i}
            className={filled ? "star-icon" : half ? "star-icon-half" : "star-icon-empty"}
            style={size ? { fontSize: size } : undefined}
            onMouseEnter={() => interactive && setHovered(score)}
            onClick={() => onSelect?.(score)}
          >
            ★
          </span>
        )
      })}
    </div>
  )
}
