import Sidebar from "./Sidebar";
import TopBar from "./TopBar";

export default function DashboardLayout({ title, children }) {
    return (
        <div className="flex h-screen overflow-hidden">
            <Sidebar />
            <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
                <TopBar title={title} />
                <main className="flex-1 overflow-y-auto p-6 bg-primary-bg animate-fade-in">
                    {children}
                </main>
            </div>
        </div>
    );
}
