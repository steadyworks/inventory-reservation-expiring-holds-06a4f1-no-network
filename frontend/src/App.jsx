import React, { useState, useEffect, useRef, useCallback } from 'react'

const API = 'http://localhost:3001'
const WS_URL = 'ws://localhost:3001/ws/inventory/'

const css = {
  app: { maxWidth: 1200, margin: '0 auto', padding: 20, fontFamily: 'system-ui, sans-serif' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '2px solid #ddd', marginBottom: 20 },
  row: { display: 'flex', gap: 20 },
  panel: { background: '#fff', borderRadius: 8, padding: 20, boxShadow: '0 1px 4px rgba(0,0,0,0.1)', marginBottom: 16 },
  h2: { fontSize: 18, fontWeight: 700, marginBottom: 16 },
  input: { width: '100%', padding: '8px 10px', border: '1px solid #ccc', borderRadius: 4, marginBottom: 10, fontSize: 14, boxSizing: 'border-box' },
  btn: { padding: '8px 16px', border: 'none', borderRadius: 4, cursor: 'pointer', fontSize: 14, fontWeight: 600 },
  primaryBtn: { background: '#0070f3', color: '#fff' },
  dangerBtn: { background: '#e00', color: '#fff' },
  successBtn: { background: '#0a0', color: '#fff' },
  disabledBtn: { background: '#ccc', color: '#888', cursor: 'not-allowed' },
  smallBtn: { padding: '4px 10px', fontSize: 12, border: '1px solid #f99', borderRadius: 4, cursor: 'pointer', fontWeight: 600, background: '#fee', color: '#c00' },
  productRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid #eee' },
  shopCard: { border: '1px solid #ddd', borderRadius: 8, padding: 16, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 16 },
  imgPlaceholder: { width: 60, height: 60, background: '#eee', borderRadius: 4, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 10, color: '#999', flexShrink: 0 },
  img: { width: 60, height: 60, objectFit: 'cover', borderRadius: 4, flexShrink: 0 },
  cartItem: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid #eee', gap: 8 },
  orderEntry: { padding: '8px 0', borderBottom: '1px solid #eee', fontSize: 13 },
  errorBox: { background: '#fee', border: '1px solid #f99', color: '#c00', padding: '10px 14px', borderRadius: 4, marginBottom: 12 },
  userBadge: { background: '#0070f3', color: '#fff', padding: '4px 12px', borderRadius: 20, fontSize: 13 },
  overlay: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 },
  modal: { background: '#fff', borderRadius: 8, padding: 32, width: 360, boxShadow: '0 4px 24px rgba(0,0,0,0.2)' },
}

export default function App() {
  return (
    <div style={css.app}>
    </div>
  )
}
