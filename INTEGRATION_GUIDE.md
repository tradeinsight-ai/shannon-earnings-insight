# earningsInsight - Integration Guide

## ✅ Phase 2 Complete: Frontend Integration

The SvelteKit frontend is now fully integrated with the FastAPI backend!

---

## 🎯 What's Working

### Backend (FastAPI)
- ✅ Alpha Vantage API integration
- ✅ Rate limiting & caching
- ✅ REST API endpoints for companies, earnings, financials, transcripts
- ✅ Error handling
- ✅ OpenAPI documentation

### Frontend (SvelteKit)
- ✅ API service layer (`src/lib/services/api.ts`)
- ✅ Real-time company search with debouncing
- ✅ Automatic data loading when company selected
- ✅ Loading states and error handling
- ✅ Fallback to mock data if API fails
- ✅ Financial data display with real API data

---

## 🚀 How to Run

### Option 1: All-in-One (Recommended)
```bash
./start_dev.sh
```

This starts both backend and frontend automatically.

### Option 2: Manual Startup

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate  # or: uv run
python -m app.main
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

---

## 🧪 Testing the Integration

1. **Start both servers** (backend on :8000, frontend on :5173)

2. **Open the app**: http://localhost:5173

3. **Test Company Search:**
   - Type "Apple" in the search box
   - Wait 500ms (debounce)
   - See real companies from Alpha Vantage API appear
   - Click "AAPL" to select

4. **Observe Data Loading:**
   - Financial Context shows "Loading financial data..."
   - After ~2 seconds, real data appears:
     - Revenue: $416.16B
     - EPS: $7.47
     - P/E Ratio: 36.64
     - Market Cap: $4.06T

5. **View Earnings History:**
   - Earnings dropdown shows real quarters from API
   - Latest: Q3 2025 (Oct 30, 2025)
   - 20 quarters of historical data

6. **Check Browser Console:**
   - No errors
   - See API calls being made
   - See data being loaded

---

## 📊 Data Flow

```
User Types "Apple"
   ↓
[Debounce 500ms]
   ↓
Frontend: searchCompaniesAPI()
   ↓
Backend: GET /api/companies/search?q=Apple
   ↓
Alpha Vantage API
   ↓
Backend: Returns companies list
   ↓
Frontend: Updates companies store
   ↓
UI: Dropdown shows results
   ↓
User Clicks "AAPL"
   ↓
Frontend: selectCompany('AAPL')
   ↓
Parallel API Calls:
   - GET /api/companies/AAPL/earnings
   - GET /api/companies/AAPL/financials
   ↓
Backend: Fetches from Alpha Vantage (with cache)
   ↓
Frontend: Updates store
   ↓
UI: Shows real financial data
```

---

## 🔧 Configuration

### Environment Variables

**Backend (`backend/.env`):**
```env
ALPHA_VANTAGE_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

**Frontend (`.env`):**
```env
VITE_API_URL=http://localhost:8000
```

---

## 🎨 UI States

### Loading States
- **Company Search**: Debounced, background loading
- **Financial Data**: Loading spinner with "Loading financial data..."
- **Earnings Calls**: Dropdown populated after load

### Error Handling
- **API Errors**: Logged to console, falls back to mock data
- **Network Errors**: User sees mock data, no UI crash
- **Rate Limiting**: Automatically handled by backend

### Success States
- **Real Data**: Displayed in Financial Context cards
- **Mock Data**: Used as fallback or for development

---

## 📝 Key Files Changed

### Frontend
- `src/lib/services/api.ts` - NEW: Backend API client
- `src/lib/stores/company.svelte.ts` - Updated with API integration
- `src/lib/components/Sidebar.svelte` - Added debounced search
- `src/lib/components/FinancialContext.svelte` - Added loading state
- `.env` - NEW: API URL configuration

### Backend
- All files created in Phase 1

---

## 🐛 Troubleshooting

### "Cannot connect to backend"
- Check backend is running: `curl http://localhost:8000/health`
- Check `.env` has correct API keys
- Check CORS is configured (it should be by default)

### "No companies found"
- Check Alpha Vantage API key is valid
- Free tier has 500 calls/day limit
- Check backend logs for errors

### "Loading forever"
- Check browser console for errors
- Check network tab for failed requests
- Verify backend is responding: `curl http://localhost:8000/api/companies/AAPL`

### "Mock data showing instead of real data"
- This is expected behavior if API fails
- Check backend logs for errors
- Verify API key is configured

---

## 🎯 Next Steps (Phase 3: AI Analysis)

1. Create AI analysis service in backend
2. Implement WebSocket for real-time streaming
3. Load transcript and analyze
4. Stream insights to frontend
5. Update AnalysisDashboard with real insights

---

## 📚 API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- API Reference: `backend/API_REFERENCE.md`

---

## ✨ Features Implemented

- [x] Backend API integration
- [x] Real-time company search
- [x] Financial data loading
- [x] Earnings history
- [x] Loading states
- [x] Error handling
- [x] Fallback to mock data
- [x] Rate limiting
- [x] Caching
- [ ] AI analysis (Phase 3)
- [ ] WebSocket streaming (Phase 3)
- [ ] Transcript analysis (Phase 3)
- [ ] Audio transcription (Phase 4)

---

**Ready to continue with Phase 3: AI Analysis?**
