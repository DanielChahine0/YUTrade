import React from 'react';

const MapsPage: React.FC = () => {
  const maps = [
    {
      name: "York University Security Services",
      description: "Located at the North East Corner of William Small Centre. This is a highly visible area with security presence nearby.",
      src: "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2881.389505863236!2d-79.50931192245281!3d43.77318517109678!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x882b2fad7ff6d1e7%3A0x404696e15987c7ed!2sYork%20University%20Security%20Services!5e1!3m2!1sen!2sca!4v1773974367958!5m2!1sen!2sca",
      image: "https://i.postimg.cc/k4WG8TzC/Screenshot_2026_03_22_at_7_18_08_PM.png"
    },
    {
      name: "Steacie Science and Engineering Library",
      description: "At the UIT (University Information Technology) Helpdesk. A busy academic environment perfect for safe daylight exchanges.",
      src: "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2475.8283581929727!2d-79.5067124141873!3d43.77360803591145!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x882b2e2fc3edf5a1%3A0x8d5c6be57936a361!2sSteacie%20Science%20and%20Engineering%20Library!5e1!3m2!1sen!2sca!4v1773976968013!5m2!1sen!2sca",
      image: "https://www.yorku.ca/uit/wp-content/uploads/sites/805/2023/12/USC-Service-Desk-Counter-v2-1-1-1536x808.jpeg"
    },
    {
      name: "Second Student Centre",
      description: "The cafeteria area in front of Break Cafe. Plenty of seating and constant foot traffic make this an ideal meeting spot.",
      src: "https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d1821.8975025882621!2d-79.50400166099962!3d43.77234403783515!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x882b2e258e6f6e4d%3A0x55e10c9ba7b8b997!2sSecond%20Student%20Centre!5e1!3m2!1sen!2sca!4v1773978167193!5m2!1sen!2sca",
      image: "https://pbs.twimg.com/media/Ggx4YlHXMAAjon3.jpg"
    },
    {
      name: "York Lanes Mall",
      description: "The seating area in the middle of the mall near Thai Express. A central retail hub with indoor security and many witnesses.",
      src: "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2862.0839191601654!2d-79.50260329621304!3d43.7741055439295!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x882b2e3fb92bab9f%3A0x86723ffa09a4721f!2sYork%20Lanes%20Mall!5e1!3m2!1sen!2sca!4v1773978770566!5m2!1sen!2sca",
      image: "https://www.yorku.ca/about/wp-content/uploads/sites/23/2020/06/DzZD1ejU0AI20JB.jpg"
    }
  ];

  return (
    <div style={{ 
      maxWidth: '1200px', 
      margin: '0 auto', 
      padding: '40px 20px',
      fontFamily: '"Segoe UI", Roboto, Helvetica, Arial, sans-serif'
    }}>
      <div style={{ marginBottom: '20px', borderBottom: '2px solid #eee', paddingBottom: '20px' }}>
        <h1 style={{ fontSize: '2.5rem', color: '#333', marginBottom: '10px' }}>Safe Meetup Locations</h1>
        <p style={{ fontSize: '1.1rem', color: '#666', lineHeight: '1.6' }}>
          We recommend meeting at these verified campus locations for all item exchanges. These spots are well-lit and typically have high foot traffic.
        </p>
      </div>

      <div style={{ 
        marginBottom: '20px', 
        padding: '30px', 
        backgroundColor: '#f8f9fa', 
        borderRadius: '12px',
        textAlign: 'center'
      }}>
        <h4 style={{ marginBottom: '10px' }}>Safety Tips</h4>
        <ul style={{ 
          listStyle: 'none', 
          padding: 0, 
          color: '#666', 
          display: 'flex', 
          flexDirection: 'column', 
          gap: '8px' 
        }}>
          <li>• Always meet during daylight hours if possible.</li>
          <li>• Bring a friend along for the exchange.</li>
          <li>• Tell someone where you are going and when you expect to be back.</li>
          <li>• Trust your instincts—if a situation feels wrong, leave immediately.</li>
        </ul>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '40px' }}>
        {maps.map((map, index) => (
          <div 
            key={index} 
            style={{ 
              backgroundColor: '#fff',
              borderRadius: '16px',
              overflow: 'hidden',
              boxShadow: '0 10px 30px rgba(0,0,0,0.08)',
              border: '1px solid #f0f0f0'
            }}
          >
            <div style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '1.5rem', color: '#222', marginBottom: '8px' }}>{map.name}</h3>
              <p style={{ color: '#555', marginBottom: '24px', lineHeight: '1.5' }}>{map.description}</p>
              
              <div style={{ 
                display: 'flex', 
                gap: '20px', 
                width: '100%',
                flexWrap: 'wrap',
                alignItems: 'stretch' 
              }}>
                <div style={{ 
                  flex: '7 1 500px',
                  minWidth: '300px',
                  borderRadius: '12px',
                  overflow: 'hidden',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
                  backgroundColor: '#f8f9fa' 
                }}>
                  <img 
                    src={map.image} 
                    alt={map.name}
                    style={{ 
                      width: '100%',
                      height: '500px', 
                      objectFit: 'contain', 
                      display: 'block'
                    }} 
                  />
                </div>
                <div style={{ 
                  flex: '3 1 350px',
                  minWidth: '300px',
                  borderRadius: '12px',
                  overflow: 'hidden',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.05)'
                }}>
                  <iframe
                    src={map.src}
                    title={map.name}
                    style={{
                      width: '100%',
                      height: '100%', 
                      minHeight: '400px',
                      border: 0,
                      display: 'block'
                    }}
                    allowFullScreen
                    loading="lazy"
                  />
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
};

export default MapsPage;
