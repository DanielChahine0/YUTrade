import React from 'react';

const MapsPage: React.FC = () => {
  const maps = [
    {
      name: "York University Security Services",
      desciption: "North East Corner of William Small Centre",
      src: "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2881.389505863236!2d-79.50931192245281!3d43.77318517109678!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x882b2fad7ff6d1e7%3A0x404696e15987c7ed!2sYork%20University%20Security%20Services!5e1!3m2!1sen!2sca!4v1773974367958!5m2!1sen!2sca"
    },
    {
      name: "Steacie Science and Engineering Library",
      desciption: "At the UIT (University Information Technology) Helpdesk ",
      src: "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2475.8283581929727!2d-79.5067124141873!3d43.77360803591145!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x882b2e2fc3edf5a1%3A0x8d5c6be57936a361!2sSteacie%20Science%20and%20Engineering%20Library!5e1!3m2!1sen!2sca!4v1773976968013!5m2!1sen!2sca",
      image: "https://www.yorku.ca/uit/wp-content/uploads/sites/805/2023/12/USC-Service-Desk-Counter-v2-1-1-1536x808.jpeg"
    },
    {
      name: "Second Student Centre",
      src: "https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d1821.8975025882621!2d-79.50400166099962!3d43.77234403783515!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x882b2e258e6f6e4d%3A0x55e10c9ba7b8b997!2sSecond%20Student%20Centre!5e1!3m2!1sen!2sca!4v1773978167193!5m2!1sen!2sca"
    },
    {
      name: "York Lanes Mall",
      src: "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2862.0839191601654!2d-79.50260329621304!3d43.7741055439295!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x882b2e3fb92bab9f%3A0x86723ffa09a4721f!2sYork%20Lanes%20Mall!5e1!3m2!1sen!2sca!4v1773978770566!5m2!1sen!2sca"
    }
  ];

  return (
    <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '50px'}}>
      <h1 style={{ paddingLeft: '10px' }}>Safe Meetup Locations</h1>
      <p style={{ paddingLeft: '10px' }}>These locations are some suggestions on where to meet on campus for exchanges!</p>
      
      {maps.map((map, index) => (
        <div key={index} style={{ width: '100%' }}>
          <h3 style={{ paddingLeft: '10px', marginBottom: '15px' }}>{map.name}</h3>
          <p style={{ paddingLeft: '10px', marginBottom: '15px' }}>{map.desciption}</p>
          <img width='1000px' src={map.image}></img>
          <iframe 
            src={map.src}
            width="1000px" 
            height="600"
            style={{ 
              border: 0, 
              display: 'block',
              boxShadow: '0 4px 12px rgba(0,0,0,0.1)' 
            }}
            allowFullScreen 
            loading="lazy"
            title={map.name}
          />
        </div>
      ))}
    </div>
  );
};

export default MapsPage;
