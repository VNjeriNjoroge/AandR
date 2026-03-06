import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [artists, setArtists] = useState([]);
  const [filteredArtists, setFilteredArtists] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [genreFilter, setGenreFilter] = useState('all');
  const [regionFilter, setRegionFilter] = useState('all');
  const [platform, setPlatform] = useState('youtube');

  useEffect(() => {
    fetch(`http://localhost:8000/api/artists/?platform=${platform}`)
      .then(response => response.json())
      .then(data => {
        setArtists(data);
        setFilteredArtists(data);
      })
      .catch(error => console.error('Error fetching data:', error));
  }, [platform]);

  useEffect(() => {
    let result = artists;

    // Filter by Search Term
    if (searchTerm) {
      result = result.filter(artist =>
        artist.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        artist.location.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by Genre
    if (genreFilter !== 'all') {
      result = result.filter(artist =>
        artist.genre.toLowerCase().includes(genreFilter.toLowerCase())
      );
    }

    // Filter by Region
    if (regionFilter !== 'all') {
      result = result.filter(artist =>
        artist.location.toLowerCase().includes(regionFilter.toLowerCase())
      );
    }

    setFilteredArtists(result);
  }, [searchTerm, genreFilter, regionFilter, artists]);

  // Helper to format numbers (e.g. 1.2M, 500K)
  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  return (
    <div className="App">
      {/* Navigation */}
      <nav className="navbar">
        <div className="nav-container">
          <div className="nav-brand">
            <span className="brand-icon">🎵</span>
            <span className="brand-name">A&R Discovery</span>
          </div>
          <ul className="nav-menu">
            <li><a href="/" className="active">Artists</a></li>
          </ul>
        </div>
      </nav>

      {/* Main Content */}
      <div className="page-container">
        <div className="page-header">
          <h1>All Artists</h1>
          <p>Browse our complete roster of tracked artists</p>
        </div>

        {/* Platform Toggle */}
        <div className="platform-toggle">
          <button
            className={`platform-btn ${platform === 'youtube' ? 'active youtube' : ''}`}
            onClick={() => setPlatform('youtube')}
          >
            ▶️ YouTube
          </button>
          <button
            className={`platform-btn ${platform === 'tiktok' ? 'active tiktok' : ''}`}
            onClick={() => setPlatform('tiktok')}
          >
            🎵 TikTok
          </button>
        </div>

        {/* Filters */}
        <div className="filters">
          <div className="filters-grid">
            <div className="filter-group">
              <span className="filter-icon">🔍</span>
              <input
                type="text"
                placeholder="Search by name or location..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <div className="filter-group">
              <span className="filter-icon">🎸</span>
              <select onChange={(e) => setGenreFilter(e.target.value)}>
                <option value="all">All Genres</option>
                <option value="afrobeats">Afrobeats</option>
                <option value="amapiano">Amapiano</option>
                <option value="hiphop">Hip-Hop/Rap</option>
                <option value="afropop">Afro-Pop</option>
              </select>
            </div>
            <div className="filter-group">
              <span className="filter-icon">📍</span>
              <select onChange={(e) => setRegionFilter(e.target.value)}>
                <option value="all">All Regions</option>
                <option value="nigeria">Nigeria</option>
                <option value="south-africa">South Africa</option>
                <option value="ghana">Ghana</option>
                <option value="kenya">Kenya</option>
              </select>
            </div>
          </div>
        </div>

        {/* Artists Grid */}
        <div className="artists-grid">
          {filteredArtists.length > 0 ? (
            filteredArtists.map(artist => (
              <div key={artist.id} className="artist-card">
                <div className="artist-header">
                  <div style={{ position: 'relative' }}>
                    <img
                      src={artist.profile_image_url || `https://ui-avatars.com/api/?name=${artist.name}&background=random`}
                      alt={artist.name}
                      className="artist-avatar"
                      referrerPolicy="no-referrer"
                    />
                    <div className="platform-badge" title={`Discovered on ${artist.discovered_on}`}>
                      {artist.discovered_on === 'tiktok' ? '🎵' : '▶️'}
                    </div>
                  </div>
                  <div className="artist-info">
                    <div className="artist-name-row">
                      <div className="artist-name">{artist.name}</div>
                      <div className={`status-badge ${artist.status?.includes('Viral') ? 'status-viral' : artist.status?.includes('Rising') ? 'status-rising' : 'status-steady'}`}>
                        {artist.status}
                      </div>
                    </div>
                    <div className="artist-genre">{artist.genre}</div>
                    <div className="artist-region">📍 {artist.location}</div>
                  </div>
                </div>

                <div className="metrics-grid">
                  <div className="metric-card">
                    <div className="metric-header">
                      <span className="metric-icon">👥</span>
                      <span className="metric-label">{platform === 'youtube' ? 'Subscribers' : 'Followers'}</span>
                    </div>
                    <div className="metric-value">
                      {formatNumber(platform === 'youtube' ? artist.current_subs : artist.tiktok_follower_count)}
                    </div>
                  </div>

                  {platform === 'youtube' ? (
                    <>
                      <div className="metric-card">
                        <div className="metric-header">
                          <span className="metric-icon">👁️</span>
                          <span className="metric-label">Total Views</span>
                        </div>
                        <div className="metric-value">{formatNumber(artist.total_views)}</div>
                      </div>
                      <div className="metric-card">
                        <div className="metric-header">
                          <span className="metric-icon">📈</span>
                          <span className="metric-label">Growth (7d)</span>
                        </div>
                        <div className={`metric-value ${artist.growth > 0 ? 'growth-positive' : 'growth-red'}`}>
                          {artist.growth > 0 ? '+' : ''}{artist.growth}%
                        </div>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="metric-card">
                        <div className="metric-header">
                          <span className="metric-icon">❤️</span>
                          <span className="metric-label">Total Likes</span>
                        </div>
                        <div className="metric-value">{formatNumber(artist.tiktok_likes)}</div>
                      </div>
                      <div className="metric-card">
                        <div className="metric-header">
                          <span className="metric-icon">🔥</span>
                          <span className="metric-label">Engagement</span>
                        </div>
                        <div className={`metric-value ${artist.engagement > 5 ? 'growth-positive' : 'growth-red'}`}>
                          {artist.engagement}%
                        </div>
                      </div>
                    </>
                  )}
                </div>

                <div className="overall-score">
                  <div>
                    <span>Viral Potential</span>
                    <div style={{ color: '#64748B', fontSize: '0.85rem', marginTop: '6px' }}>
                      Status: <strong style={{ color: artist.viral_label === 'High' ? '#1DB954' : '#C0C0C0' }}>{artist.viral_label}</strong>
                    </div>
                  </div>
                  <span>{artist.viral_score}</span>
                </div>

                <div style={{ padding: '0 25px 25px' }}>
                  <a
                    href={platform === 'youtube' ? `https://youtube.com/channel/${artist.youtube_channel_id}` : `https://tiktok.com/${artist.tiktok_handle}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="view-channel-btn"
                  >
                    View {platform === 'youtube' ? 'Channel' : 'Profile'}
                  </a>
                </div>
              </div>
            ))
          ) : (
            <div className="no-results">No artists found matching your criteria.</div>
          )}
        </div>
      </div>

    </div>
  );
}

export default App;
