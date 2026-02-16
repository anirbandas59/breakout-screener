/**
 * Type re-export bridge.
 *
 * API response types are generated from the FastAPI OpenAPI schema.
 * Run `npm run generate-types` to regenerate api.generated.ts.
 *
 * Until the generated file is populated, types fall back to the manually
 * maintained AppInterfaces.ts definitions below.
 *
 * Component prop types remain in AppInterfaces.ts.
 */

// Re-export generated API types (populated by npm run generate-types)
export type { components } from './api.generated';

// Re-export manual types until generation is set up
// These will be superseded by the generated types once api.generated.ts is populated
export type {
  DataRow,
  DataResponse,
  APIResponse,
  TaskResponse,
  GeneralResponse,
  ButtonGroupsProps,
  DataTableProps,
  InputFormProps,
  TaskProgress,
} from './AppInterfaces';
