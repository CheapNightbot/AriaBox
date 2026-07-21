import { Button } from "@/components/ui/button"
import {
    Dialog,
    DialogClose,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger
} from "@/components/ui/dialog"

export default function LegalAndDisclaimer() {
    return (
        <Dialog>
            <DialogTrigger asChild>
                <Button variant="link" className="text-xs text-muted-foreground">
                    Legal & Disclaimer
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-125">
                <DialogHeader>
                    <DialogTitle>Legal & Disclaimer</DialogTitle>
                    <DialogDescription>
                        AriaBox is an independent, open-source tool designed to help you manage and organize your personal music library.
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-4 py-4 text-sm text-muted-foreground">
                    <p>
                        <strong>Core Purpose:</strong> AriaBox helps you add and update music metadata, convert between audio formats, and keep your collection beautifully organized. It is not affiliated with, endorsed by, or connected to Deezer, Apple Music, YouTube Music, or any other music service.
                    </p>
                    <p>
                        <strong>Optional Downloads & Ethics:</strong> The optional downloading feature is provided strictly as a fallback for hard-to-find tracks (such as rare cover songs) and to offer a safe, clean alternative to sketchy download sites. We strongly encourage you to support your favorite artists by purchasing their music or streaming it on official platforms whenever possible.
                    </p>
                    <p>
                        <strong>Your Privacy:</strong> All processing, including metadata fetching, audio conversion, and downloading, happens locally on your machine or private server. AriaBox does not collect, store, or transmit your personal data, search history, or music library to any third party.
                    </p>
                </div>

                <DialogFooter>
                    <DialogClose asChild>
                        <Button type="button" variant="secondary">
                            Understood
                        </Button>
                    </DialogClose>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
