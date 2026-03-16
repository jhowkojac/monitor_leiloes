import { Header } from './components/Header';
import { HeroSection } from './components/HeroSection';
import { FilterSection } from './components/FilterSection';
import { AuctionGrid } from './components/AuctionGrid';

function App() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main>
        <HeroSection />
        <FilterSection />
        <AuctionGrid />
      </main>
    </div>
  );
}

export default App;
