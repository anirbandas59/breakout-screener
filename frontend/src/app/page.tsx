import Header from '@/components/Header/Header';

export default function Home() {
  return (
    <div className="">
      <Header />
      <main className="flex flex-col gap-8 row-start-2 items-center sm:items-start">
        Main Section
      </main>
    </div>
  );
}
