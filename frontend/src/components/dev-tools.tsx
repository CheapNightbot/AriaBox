// Only use during developemnt please !!!

import { Button } from "@/components/ui/button"
import {
    Dialog,
    DialogClose,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow
} from "@/components/ui/table"
import {
    Tooltip,
    TooltipContent,
    TooltipTrigger,
} from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"
import { BrushCleaningIcon, RefreshCwIcon, WrenchIcon } from "lucide-react"
import { useEffect, useState } from "react"
import { toast } from "sonner"

interface CacheStats {
    total_entries: number,
    search_queries: number,
    individual_items: number,
    memory_estimate_kb: number,
}

interface CacheClear {
    message: string
}

export default function DevTools() {
    const [cacheStats, setCacheStats] = useState<CacheStats | null>(null)
    const [error, setError] = useState<string | null>(null)
    const [loading, setLoading] = useState(true)

    const getCacheStats = async () => {
        try {
            setLoading(true)
            const response = await fetch("/api/cache/stats")
            if (!response.ok) {
                throw new Error("Couldn't fetch cache stats! Click on refresh button or check server logs.")
            }
            const data = await response.json() as CacheStats
            setCacheStats(data)
        } catch (e) {
            if (e instanceof Error) setError(e.message)
        } finally {
            setTimeout(() => {
                setLoading(false)
            }, 1000)
        }
    }

    const clearCache = async () => {
        try {
            const response = await fetch("/api/cache/clear", { method: "POST" })
            if (!response.ok) {
                throw new Error("Couldn't clear cache! Try again or check the server logs.")
            }
            const data = await response.json() as CacheClear
            toast.success(data.message)
        } catch (e) {
            if (e instanceof Error) toast.error(e.message)
        }
    }

    useEffect(() => {
        getCacheStats()
    }, [])

    return (
        <Dialog onOpenChange={(open) => { if (open) getCacheStats() }}>
            <DialogTrigger>
                <Tooltip delayDuration={500}>
                    <TooltipTrigger asChild>
                        <Button asChild size="icon" variant="ghost" className="p-2">
                            <WrenchIcon />
                        </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                        <p>Dev Tools</p>
                    </TooltipContent>
                </Tooltip>
            </DialogTrigger>
            <DialogContent className="sm:max-w-xl" onOpenAutoFocus={(e) => e.preventDefault()}>
                <DialogHeader>
                    <DialogTitle className="text-xl">Dev Tools</DialogTitle>
                    <DialogDescription>
                        Useful information & tools during development ~
                    </DialogDescription>
                </DialogHeader>
                <section>
                    <div className="flex items-center justify-between gap-2">
                        <h3 className="text-lg font-semibold">Cache Stats</h3>
                        <div className="flex items-center gap-2">
                            <Tooltip delayDuration={500}>
                                <TooltipTrigger>
                                    <Button
                                        asChild
                                        className={cn("p-2", loading && "animate-spin hover:bg-transparent")}
                                        disabled={loading}
                                        size="icon-sm"
                                        variant="ghost"
                                        onClick={getCacheStats}
                                    >
                                        <RefreshCwIcon />
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent side="left">
                                    <p>{loading ? "Refreshing" : "Refresh"}</p>
                                </TooltipContent>
                            </Tooltip>

                            <Tooltip delayDuration={500}>
                                <TooltipTrigger>
                                    <Button
                                        asChild
                                        className="p-2"
                                        disabled={loading}
                                        size="icon-sm"
                                        variant="ghost"
                                        onClick={clearCache}
                                    >
                                        <BrushCleaningIcon />
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent side="left">
                                    <p>Clear</p>
                                </TooltipContent>
                            </Tooltip>
                        </div>
                    </div>
                    {cacheStats
                        ? <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead className="whitespace-normal wrap-break-word">Total Entries</TableHead>
                                    <TableHead className="whitespace-normal wrap-break-word">Search Queries</TableHead>
                                    <TableHead className="whitespace-normal wrap-break-word">Individual Items</TableHead>
                                    <TableHead className="whitespace-normal wrap-break-word">Memory Estimate (kb)</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                <TableRow>
                                    <TableCell>{cacheStats.total_entries}</TableCell>
                                    <TableCell>{cacheStats.search_queries}</TableCell>
                                    <TableCell>{cacheStats.individual_items}</TableCell>
                                    <TableCell>{cacheStats.memory_estimate_kb}</TableCell>
                                </TableRow>
                            </TableBody>
                        </Table>
                        : <p>{error}</p>
                    }
                </section>
                <DialogFooter>
                    <DialogClose asChild><Button variant="outline">Close</Button></DialogClose>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
