import * as access_control from "./codegen";

export interface CreateUserArgs {
  userId: string;
  group?:
    | {
        newGroup: {
          name: string;
          description?: string;
          parent?: string;
        };
      }
    | string;
}

type CreateUserOnlySuccess = {
  result: "success";
  data: {
    user: {
      id: string;
    };
  };
};

type CreateUserGroupSuccess = {
  result: "success";
  data: {
    user: {
      id: string;
    };
    group: {
      id: string;
    };
  };
};

export type CreateUserResults =
  | { result: "error"; data: "string" }
  | CreateUserOnlySuccess
  | CreateUserGroupSuccess;

async function createUser(
  userArgs: Pick<CreateUserArgs, "userId"> // only create user, use default group
): Promise<CreateUserOnlySuccess>;
async function createUser(
  userArgs: Required<CreateUserArgs> // create user and group
): Promise<CreateUserGroupSuccess>;
async function createUser(
  userArgs: Pick<CreateUserArgs, "userId"> & { group: string } // create user and assign group
): Promise<CreateUserOnlySuccess>;
async function createUser(
  userArgs: CreateUserArgs
): Promise<CreateUserResults> {
  access_control.accessControlUsersCreate({
    body: {
      user_id: userArgs.userId,
    },
  });
  return {
    result: "success",
    data: {
      user: { id: "123" },
      group: { id: "123" },
    },
  };
}
