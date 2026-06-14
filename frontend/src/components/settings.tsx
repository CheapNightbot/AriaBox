import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldSet,
} from "@/components/ui/field";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { fetchSettings, updateSettings } from "@/lib/api";
import type { AppSettings } from "@/types";
import { useEffect, useState } from "react";
import { toast } from "sonner";

const availableLanguages = {
  ar: "Arabic",
  de: "German",
  en: "English",
  es: "Spanish",
  fr: "French",
  hi: "Hindi",
  it: "Italian",
  ja: "Japanese",
  ko: "Korean",
  nl: "Dutch",
  pt: "Portuguese",
  ru: "Russian",
  tr: "Turkish",
  ur: "Urdu",
  zh_CN: "Chinese (Mainland)",
  zh_TW: "Chinese (Taiwan)",
};

const availableLocations = {
  DZ: "Algeria",
  AR: "Argentina",
  AU: "Australia",
  AT: "Austria",
  AZ: "Azerbaijan",
  BH: "Bahrain",
  BD: "Bangladesh",
  BY: "Belarus",
  BE: "Belgium",
  BO: "Bolivia",
  BA: "Bosnia and Herzegovina",
  BR: "Brazil",
  BG: "Bulgaria",
  KH: "Cambodia",
  CA: "Canada",
  CL: "Chile",
  CO: "Colombia",
  CR: "Costa Rica",
  HR: "Croatia",
  CY: "Cyprus",
  CZ: "Czechia",
  DK: "Denmark",
  DO: "Dominican Republic",
  EC: "Ecuador",
  EG: "Egypt",
  SV: "El Salvador",
  EE: "Estonia",
  FI: "Finland",
  FR: "France",
  GE: "Georgia",
  DE: "Germany",
  GH: "Ghana",
  GR: "Greece",
  GT: "Guatemala",
  HN: "Honduras",
  HK: "Hong Kong",
  HU: "Hungary",
  IS: "Iceland",
  IN: "India",
  ID: "Indonesia",
  IQ: "Iraq",
  IE: "Ireland",
  IL: "Israel",
  IT: "Italy",
  JM: "Jamaica",
  JP: "Japan",
  JO: "Jordan",
  KZ: "Kazakhstan",
  KE: "Kenya",
  KW: "Kuwait",
  LA: "Laos",
  LV: "Latvia",
  LB: "Lebanon",
  LY: "Libya",
  LI: "Liechtenstein",
  LT: "Lithuania",
  LU: "Luxembourg",
  MY: "Malaysia",
  MT: "Malta",
  MX: "Mexico",
  ME: "Montenegro",
  MA: "Morocco",
  NP: "Nepal",
  NL: "Netherlands",
  NZ: "New Zealand",
  NI: "Nicaragua",
  NG: "Nigeria",
  MK: "North Macedonia",
  NO: "Norway",
  OM: "Oman",
  PK: "Pakistan",
  PA: "Panama",
  PG: "Papua New Guinea",
  PY: "Paraguay",
  PE: "Peru",
  PH: "Philippines",
  PL: "Poland",
  PT: "Portugal",
  PR: "Puerto Rico",
  QA: "Qatar",
  RO: "Romania",
  RU: "Russia",
  SA: "Saudi Arabia",
  SN: "Senegal",
  RS: "Serbia",
  SG: "Singapore",
  SK: "Slovakia",
  SI: "Slovenia",
  ZA: "South Africa",
  KR: "South Korea",
  ES: "Spain",
  LK: "Sri Lanka",
  SE: "Sweden",
  CH: "Switzerland",
  TW: "Taiwan",
  TZ: "Tanzania",
  TH: "Thailand",
  TN: "Tunisia",
  TR: "Turkey",
  UG: "Uganda",
  UA: "Ukraine",
  AE: "United Arab Emirates",
  GB: "United Kingdom",
  US: "United States",
  UY: "Uruguay",
  VE: "Venezuela",
  VN: "Vietnam",
  YE: "Yemen",
  ZW: "Zimbabwe",
};

function Settings() {
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadSettings() {
      try {
        const data = await fetchSettings();
        setSettings(data);
      } catch (error) {
        const msg = error instanceof Error ? error.message : "Unknown error";
        toast.error(`Failed to fetch settings: ${msg}`);
      } finally {
        setIsLoading(false);
      }
    }
    loadSettings();
  }, []);

  const handleLanguageChange = async (newLang: string) => {
    if (!settings) return;
    try {
      const updatedData = await updateSettings({ language: newLang });
      setSettings(updatedData);
      toast.success("Response language has been updated! ദ്ദി(˵ •̀ ᴗ - ˵ ) ✧");
    } catch (error) {
      const msg = error instanceof Error ? error.message : "Unknown error";
      toast.error(`Failed to update language: ${msg}`);
    }
  };

  const handleLocationChange = async (newLoc: string) => {
    if (!settings) return;
    try {
      const updatedData = await updateSettings({ location: newLoc });
      setSettings(updatedData);
      toast.success("Location has been updated! ദ്ദി(˵ •̀ ᴗ - ˵ ) ✧");
    } catch (error) {
      const msg = error instanceof Error ? error.message : "Unknown error";
      toast.error(`Failed to update location: ${msg}`);
    }
  };

  return (
    <ScrollArea className="border h-[clamp(600px,85vh,830px)] w-[clamp(600px,90vw,1200px)] rounded-sm pt-8">
      {isLoading ? (
        <div className="h-[clamp(600px,70vh,700px)] w-full grid place-items-center">
          <p className="text-xl text-muted-foreground animate-in fade-in-60 zoom-in-80 duration-500 ease-in-out">
            <span className="animate-pulse">Loading settings...𓏲 ๋࣭ ࣪ ˖🎐</span>
          </p>
        </div>
      ) : !settings ? (
        <div className="h-[clamp(600px,70vh,700px)] w-full grid place-items-center">
          <p className="text-xl text-muted-foreground animate-in fade-in-60 zoom-in-80 duration-500 ease-in-out">
            Could not load settings.
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-6 items-center animate-in zoom-in-95 fade-in ease-in-out duration-500">
          <h2 className="scroll-m-20 pb-2 text-3xl font-semibold tracking-tight first:mt-0 w-[clamp(600px,60vw,800px)]">
            Settings
          </h2>

          <FieldSet className="w-[clamp(600px,60vw,800px)]">
            <FieldDescription>
              These settings affect the response language and location. Note
              that not all music services respect these settings.
            </FieldDescription>
            <FieldGroup className="gap-6">
              <Field>
                <Label htmlFor="language">Language</Label>
                <Select
                  value={settings.language}
                  onValueChange={handleLanguageChange}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Language to return results in..." />
                  </SelectTrigger>
                  <SelectContent position="popper">
                    <SelectGroup>
                      {Object.entries(availableLanguages).map(
                        ([key, value]) => (
                          <SelectItem key={key} value={key}>
                            {value}
                          </SelectItem>
                        ),
                      )}
                    </SelectGroup>
                  </SelectContent>
                </Select>
              </Field>

              <Field>
                <Label htmlFor="location">Location</Label>
                <Select
                  value={settings.location}
                  onValueChange={handleLocationChange}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Location to use to fetch results from..." />
                  </SelectTrigger>
                  <SelectContent position="popper">
                    <SelectGroup>
                      {Object.entries(availableLocations).map(
                        ([key, value]) => (
                          <SelectItem key={key} value={key}>
                            {value}
                          </SelectItem>
                        ),
                      )}
                    </SelectGroup>
                  </SelectContent>
                </Select>
              </Field>
            </FieldGroup>
          </FieldSet>
        </div>
      )}
    </ScrollArea>
  );
}

export default Settings;
