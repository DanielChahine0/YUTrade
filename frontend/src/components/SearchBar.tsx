// Assigned to: Harnaindeep Kaur
// Phase: 3 (F3.5)
//
// TODO: Search and filter bar for the BrowsePage.
//
// Props:
//   - onSearch(params: { search?, category?, min_price?, max_price? }): void
//       Callback to trigger a new search in BrowsePage
//
// Structure:
//   <div className="search-bar">
//     <input type="text" placeholder="Search listings..." value={search} onChange={...} />
//     <select value={category} onChange={...}>
//       <option value="">All Categories</option>
//       <option value="Textbooks">Textbooks</option>
//       <option value="Electronics">Electronics</option>
//       <option value="Furniture">Furniture</option>
//       <option value="Clothing">Clothing</option>
//       <option value="Other">Other</option>
//     </select>
//     <input type="number" placeholder="Min Price" value={minPrice} onChange={...} />
//     <input type="number" placeholder="Max Price" value={maxPrice} onChange={...} />
//     <button onClick={handleSearch}>Search</button>
//   </div>
//
// Behavior:
//   1. Maintain local state for search, category, minPrice, maxPrice
//   2. On "Search" click (or Enter key), call onSearch with current filter values
//   3. Omit empty/null values from the params object
//   4. Optional: debounce text input for live search
//
// Styling: Horizontal bar, inputs side by side, responsive (stack on mobile)



import React, { useState } from "react";

type SearchParams = {
  search?: string;
  category?: string;
  min_price?: number;
  max_price?: number;
  sort?: string;
  date_listed?: string;
};

type Props = {
  onSearch: (params: SearchParams) => void;
};

const SearchBar: React.FC<Props> = ({ onSearch }) => {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [sort, setSort] = useState("newest");
  const [dateListed, setDateListed] = useState("");

  const handleSearch = () => {
    const params: SearchParams = {};
    if (search.trim()) params.search = search.trim();
    if (category) params.category = category;
    if (minPrice) params.min_price = Number(minPrice);
    if (maxPrice) params.max_price = Number(maxPrice);
    if (sort) params.sort = sort;
    if (dateListed) params.date_listed = dateListed;

    onSearch(params);
  };

  const handleReset = () => {
    setSearch("");
    setCategory("");
    setMinPrice("");
    setMaxPrice("");
    setSort("newest");
    setDateListed("");
    onSearch({}); // reset search results
  };

  return (
    <div className="search-bar">
      <div className="inputs-group">
        <input
          type="text"
          placeholder="Search listings..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="">All Categories</option>
          <option value="Textbooks">Textbooks</option>
          <option value="Electronics">Electronics</option>
          <option value="Furniture">Furniture</option>
          <option value="Clothing">Clothing</option>
          <option value="Other">Other</option>
        </select>

        <input
          type="number"
          placeholder="Min"
          value={minPrice}
          onChange={(e) => setMinPrice(e.target.value)}
        />

        <input
          type="number"
          placeholder="Max"
          value={maxPrice}
          onChange={(e) => setMaxPrice(e.target.value)}
        />

        <select value={sort} onChange={(e) => setSort(e.target.value)}>
          <option value="newest">Newest</option>
          <option value="price_low_to_high">Low → High</option>
          <option value="price_high_to_low">High → Low</option>
        </select>

        <select value={dateListed} onChange={(e) => setDateListed(e.target.value)}>
          <option value="">Any time</option>
          <option value="last_24_hours">24h</option>
          <option value="last_7_days">7 days</option>
          <option value="last_30_days">30 days</option>
        </select>
      </div>

      <div style={{ display: "flex", gap: "8px" }}>
        <button onClick={handleSearch}>Search</button>
        <button
          onClick={handleReset}
          style={{
            background: "#555",
            color: "#fff",
            padding: "6px 12px",
            fontSize: "12px",
            borderRadius: "8px",
            cursor: "pointer",
          }}
        >
          Reset Filters
        </button>
      </div>
    </div>
  );
};

export default SearchBar;