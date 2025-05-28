// KakaoMap.jsx
import React, { useEffect, useRef } from "react";

const KakaoMapView  = () => {
  const mapRef = useRef(null); //useRef로 div 참조
  const kakaoApiKey = import.meta.env.VITE_KAKAO_MAP_API_KEY;

  useEffect(() => {
    const script = document.createElement("script");
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${kakaoApiKey}&autoload=false`;
    script.async = true;

    script.onload = () => {
      window.kakao.maps.load(() => {
        const options = {
          center: new window.kakao.maps.LatLng(37.5665, 126.9780),
          level: 3,
        };
        new window.kakao.maps.Map(mapRef.current, options); //여기서 ref 사용
      });
    };

    

    document.head.appendChild(script);
  }, []);

  return (
    <div
      ref={mapRef} //여기 연결
      style={{ width: "100%", height: "400px", border: "1px solid #ddd" }}
    ></div>
  );
};

export default KakaoMapView;