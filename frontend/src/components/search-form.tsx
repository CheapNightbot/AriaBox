import { searchMusic } from "@/lib/api";
import type { SearchResults } from "@/types";
import type { SubmitHandler } from "@formisch/react";
import { Form, Field as FormischField, reset, useForm } from "@formisch/react";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import * as v from "valibot";

import { Button } from "@/components/ui/button";
import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Spinner } from "@/components/ui/spinner";
import { AudioLinesIcon, MusicIcon, UserIcon } from "lucide-react";

const NameSchema = v.pipe(
  v.object({
    artist: v.exactOptional(v.pipe(v.string(), v.trim())),
    song: v.exactOptional(v.pipe(v.string(), v.trim())),
  }),
  v.check(
    (input) => !!(input.artist ?? input.song),
    "Please enter an Artist name, a Song title, or both. At least one field is required.",
  ),
);

const UrlSchema = v.object({
  music_url: v.pipe(
    v.string(),
    v.nonEmpty("Please enter your URL."),
    v.url("Please enter a valid URL starting with http:// or https://."),
  ),
});

function SearchForm({
  loading,
  setLoading,
  setResults,
}: {
  loading: boolean;
  setLoading: React.Dispatch<React.SetStateAction<boolean>>;
  setResults: React.Dispatch<React.SetStateAction<SearchResults>>;
}) {
  const artistInputRef = useRef<HTMLInputElement>(null);
  const urlInputRef = useRef<HTMLInputElement>(null);

  const [searchMethod, setSearchMethod] = useState<
    "named_search" | "url_search"
  >("named_search");

  // Initialize both forms
  const nameForm = useForm({
    schema: NameSchema,
    initialInput: { artist: "", song: "" },
  });

  const urlForm = useForm({
    schema: UrlSchema,
    initialInput: { music_url: "" },
  });

  useEffect(() => {
    if (
      searchMethod === "named_search" &&
      nameForm.errors &&
      nameForm.errors.length > 0
    ) {
      const error = nameForm.errors[0];
      const errorMessage =
        typeof error === "string"
          ? error
          : ((error as { message?: string }).message ?? "Validation error");
      toast.error(errorMessage);
    }
  }, [nameForm.errors]);

  // Single shared function for the API call!
  const handleSearch = async (payload: {
    artist?: string;
    song?: string;
    music_url?: string;
  }) => {
    try {
      setLoading(true);

      const results = await searchMusic({
        ...payload,
        search_method: searchMethod,
      });

      setResults(results);
    } catch (error) {
      if (error instanceof Error) {
        toast.error(error.message);
      } else {
        toast.error("An unexpected error occurred");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleNameSubmit: SubmitHandler<typeof NameSchema> = async (output) => {
    await handleSearch(output);
  };

  const handleUrlSubmit: SubmitHandler<typeof UrlSchema> = async (output) => {
    await handleSearch(output);
  };

  const setFocus = () => {
    setTimeout(() => {
      if (searchMethod === "named_search") {
        artistInputRef?.current?.focus();
      } else if (searchMethod === "url_search") {
        urlInputRef?.current?.focus();
      }
    }, 200);
  };

  const handleMethodChange = (value: string) => {
    const newMethod = value as "named_search" | "url_search";
    setSearchMethod(newMethod);
    setFocus();

    // Reset the form
    if (newMethod === "named_search") reset(urlForm);
    else reset(nameForm);
  };

  // Set the focus to correct input on load
  setFocus();

  return (
    <div className="w-[clamp(400px,90vw,1200px)] py-3 h-30">
      <FieldGroup className="flex flex-row gap-4 items-start justify-center">
        <Select value={searchMethod} onValueChange={handleMethodChange}>
          <SelectTrigger>
            <SelectValue placeholder="Search by..." />
          </SelectTrigger>
          <SelectContent position="popper">
            <SelectItem value="named_search">Artist / Song</SelectItem>
            <SelectItem value="url_search">Music URL</SelectItem>
          </SelectContent>
        </Select>

        {searchMethod === "named_search" ? (
          <Form
            of={nameForm}
            id="name-search"
            onSubmit={handleNameSubmit}
            className="contents"
          >
            <FormischField of={nameForm} path={["artist"]}>
              {(field) => (
                <Field data-invalid={field.errors !== null}>
                  <FieldLabel htmlFor="name-search-artist" className="sr-only">
                    Artist
                  </FieldLabel>
                  <InputGroup>
                    <InputGroupInput
                      {...field.props}
                      ref={artistInputRef}
                      id="name-search-artist"
                      value={field.input ?? ""}
                      aria-invalid={field.errors !== null}
                      placeholder="Artist Name"
                      autoComplete="off"
                    />
                    <InputGroupAddon>
                      <UserIcon />
                    </InputGroupAddon>
                  </InputGroup>
                  {field.errors && (
                    <FieldError
                      errors={field.errors.map((message) => ({ message }))}
                    />
                  )}
                </Field>
              )}
            </FormischField>

            <FormischField of={nameForm} path={["song"]}>
              {(field) => (
                <Field data-invalid={field.errors !== null}>
                  <FieldLabel htmlFor="name-search-song" className="sr-only">
                    Song
                  </FieldLabel>
                  <InputGroup>
                    <InputGroupInput
                      {...field.props}
                      id="name-search-song"
                      value={field.input ?? ""}
                      aria-invalid={field.errors !== null}
                      placeholder="Song Title"
                      autoComplete="off"
                    />
                    <InputGroupAddon>
                      <MusicIcon />
                    </InputGroupAddon>
                  </InputGroup>
                  {field.errors && (
                    <FieldError
                      errors={field.errors.map((message) => ({ message }))}
                    />
                  )}
                </Field>
              )}
            </FormischField>

            <Field orientation="horizontal" className="flex-0">
              <Button type="submit" form="name-search" disabled={loading}>
                {loading ? (
                  <>
                    <Spinner data-icon="inline-start" />
                    Searching
                  </>
                ) : (
                  "Search"
                )}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => reset(nameForm)}
                disabled={loading}
              >
                Reset
              </Button>
            </Field>
          </Form>
        ) : (
          <Form
            of={urlForm}
            id="url-search"
            onSubmit={handleUrlSubmit}
            className="contents"
          >
            <FormischField of={urlForm} path={["music_url"]}>
              {(field) => (
                <Field data-invalid={field.errors !== null}>
                  <FieldLabel htmlFor="url-search-music" className="sr-only">
                    Music URL
                  </FieldLabel>
                  <InputGroup>
                    <InputGroupInput
                      {...field.props}
                      ref={urlInputRef}
                      id="url-search-music"
                      value={field.input ?? ""}
                      aria-invalid={field.errors !== null}
                      placeholder="You can enter Deezer or YouTube Music URL here..."
                      autoComplete="off"
                    />
                    <InputGroupAddon>
                      <AudioLinesIcon />
                    </InputGroupAddon>
                  </InputGroup>
                  {field.errors && (
                    <FieldError
                      errors={field.errors.map((message) => ({ message }))}
                    />
                  )}
                </Field>
              )}
            </FormischField>

            <Field orientation="horizontal" className="flex-0">
              <Button type="submit" form="url-search" disabled={loading}>
                {loading ? (
                  <>
                    <Spinner data-icon="inline-start" />
                    Searching
                  </>
                ) : (
                  "Search"
                )}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => reset(urlForm)}
                disabled={loading}
              >
                Reset
              </Button>
            </Field>
          </Form>
        )}
      </FieldGroup>
    </div>
  );
}

export default SearchForm;
