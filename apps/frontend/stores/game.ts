import { computed, ref } from "vue";
import { defineStore } from "pinia";

import {
  useGameApi,
  type GameStatus,
  type NextTurn,
} from "~/composables/useGameApi";
import { useTelegramWebApp } from "~/composables/useTelegramWebApp";

const UNEXPECTED_ERROR = "Непредвиденная ошибка";

const emptyBoard = (): string[] => Array.from({ length: 9 }, () => "");

const toErrorMessage = (err: unknown): string => {
  if (err instanceof Error && err.message) return err.message;
  return UNEXPECTED_ERROR;
};

type GameResponse = {
  board: string[];
  status: GameStatus;
  next: NextTurn;
  promoCode?: string | null;
};

export const useGameStore = defineStore("game", () => {
  const api = useGameApi();
  const telegram = useTelegramWebApp();

  const board = ref<string[]>(emptyBoard());
  const status = ref<GameStatus>("in_progress");
  const next = ref<NextTurn>("player");
  const promoCode = ref<string | null>(null);

  const error = ref<string | null>(null);
  const isReady = ref(false);

  // Раздельные флаги, чтобы UI мог корректно отличать reset от "ИИ думает"
  const isHydrating = ref(false);
  const isMoving = ref(false);

  const isLoading = computed(() => isHydrating.value || isMoving.value);

  const isBoardLocked = computed(() => status.value !== "in_progress");
  const hasResult = computed(() => status.value !== "in_progress");

  const resultTitle = computed(() => {
    if (status.value === "win") return "Ура! Ты победила";
    if (status.value === "lose") return "Заберём реванш?";
    if (status.value === "draw") return "Ничья";
    return "";
  });

  const resultDescription = computed(() => {
    if (status.value === "win") {
      return "Забери свой промокод и добавь немного роскоши в день.";
    }
    if (status.value === "lose") {
      return "Не переживай: пара шагов в новом темпе — и победа будет на твоей стороне.";
    }
    if (status.value === "draw") {
      return "Всё честно: обнови поле и попробуй с новой тактикой.";
    }
    return "";
  });

  const applyResponse = (payload: GameResponse) => {
    board.value = [...payload.board];
    status.value = payload.status;
    next.value = payload.next;
    promoCode.value = payload.promoCode ?? null;
  };

  const applyResetFallback = () => {
    board.value = emptyBoard();
    status.value = "in_progress";
    next.value = "player";
    promoCode.value = null;
  };

  const playerMove = async (index: number) => {
    // Жёсткие предохранители от неправильных кликов и гонок
    if (isLoading.value) return;
    if (isBoardLocked.value) return;
    if (board.value[index]) return;

    isMoving.value = true;
    error.value = null;

    try {
      const response = await api.makeMove({
        board: board.value,
        moveIndex: index,
        initData: telegram.initData.value ?? undefined,
        chatId: telegram.chatId.value ?? undefined,
      });

      applyResponse(response);

      // Хаптик — best-effort
      telegram.triggerHaptic(response.status === "win" ? "medium" : "light");
    } catch (err) {
      error.value = toErrorMessage(err);
    } finally {
      isMoving.value = false;
    }
  };

  const resetGame = async () => {
    if (isLoading.value) return;

    isHydrating.value = true;
    error.value = null;

    try {
      const response = await api.resetGame();
      applyResponse(response);

      // reset должен гарантированно очищать промокод
      promoCode.value = null;
    } catch (err) {
      applyResetFallback();
      error.value = toErrorMessage(err);
    } finally {
      isHydrating.value = false;
      isReady.value = true;
    }
  };

  const bootstrap = async () => {
    if (isReady.value) return;
    await resetGame();
  };

  return {
    board,
    status,
    next,
    promoCode,

    error,
    isReady,

    isHydrating,
    isMoving,
    isLoading,

    isBoardLocked,
    hasResult,

    resultTitle,
    resultDescription,

    playerMove,
    resetGame,
    bootstrap,
  };
});
