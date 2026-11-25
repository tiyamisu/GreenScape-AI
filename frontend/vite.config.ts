import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({plugins:[react()],server:{port:5173},build:{target:'es2022',rollupOptions:{output:{manualChunks(id){
  if(id.includes('/node_modules/three/')) return 'three';
  if(id.includes('/node_modules/@react-three/')) return 'r3f';
  if(id.includes('/node_modules/react-dom/')||id.includes('/node_modules/react/')) return 'react';
  if(id.includes('/node_modules/lucide-react/')) return 'icons';
}}}}});
