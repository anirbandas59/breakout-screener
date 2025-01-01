'use client';

import DataTable from '@/components/DataTable/DataTable';
import Header from '@/components/Header/Header';
import InputForm from '@/components/InputForm/InputForm';

export default function Home() {
  return (
    <div className="font-sans">
      <Header />
      <main className="flex flex-1 gap-2 row-start-2 items-center sm:items-start">
        <div className="">
          <InputForm />
        </div>
        <div className="flex-1 my-2">
          <DataTable />
        </div>
      </main>
    </div>
  );
}
